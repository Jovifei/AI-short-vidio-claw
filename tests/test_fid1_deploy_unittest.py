import hashlib
import importlib
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUDIT = ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source"


def make_comfy_root(root):
    comfy = root / "ComfyUI"
    comfy.mkdir()
    (comfy / "custom_nodes").mkdir()
    for rel in ("comfy_extras/nodes_wan.py", "comfy/latent_formats.py", "comfy/samplers.py", "comfy/sample.py", "LICENSE"):
        target = comfy / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE_AUDIT / rel, target)
    return comfy


class FID1DeployTests(unittest.TestCase):
    def module(self):
        self.assertTrue((ROOT / "scripts/fid1_deploy.py").is_file(), "FID1 deployment must have an explicit local installer")
        return importlib.import_module("scripts.fid1_deploy")

    def test_deploy_is_exact_and_idempotent_then_rolls_back_only_its_package(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            unrelated = comfy / "custom_nodes/existing_node.py"
            unrelated.write_text("owner custom node\n", encoding="utf-8")

            first = deploy.deploy(root, comfy)
            target = comfy / "custom_nodes/fid1_wan_roi_anchor/__init__.py"
            self.assertEqual(first["status"], "INSTALLED")
            self.assertEqual(target.read_bytes(), (root / "scripts/fid1_wan_latent_anchor_node.py").read_bytes())
            first_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            second = deploy.deploy(root, comfy)
            self.assertEqual(second["status"], "ALREADY_INSTALLED")
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), first_hash)

            rolled_back = deploy.rollback(root, comfy)
            self.assertEqual(rolled_back["status"], "ROLLED_BACK")
            self.assertFalse((comfy / "custom_nodes/fid1_wan_roi_anchor").exists())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "owner custom node\n")

    def test_conflicting_plugin_directory_is_not_overwritten(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            target = comfy / "custom_nodes/fid1_wan_roi_anchor"
            target.mkdir()
            owned = target / "__init__.py"
            owned.write_text("pre-existing owner file\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "conflict|owned|manifest"):
                deploy.deploy(root, comfy)
            self.assertEqual(owned.read_text(encoding="utf-8"), "pre-existing owner file\n")

    def test_runtime_dependency_mismatch_blocks_install(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            samplers = comfy / "comfy/samplers.py"
            samplers.write_text(samplers.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ComfyUI|dependency|hash"):
                deploy.deploy(root, comfy)
            self.assertFalse((comfy / "custom_nodes/fid1_wan_roi_anchor").exists())

    def test_comfy_contract_accepts_lf_checkout_of_same_audited_source(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            installed = comfy / "comfy_extras/nodes_wan.py"
            installed.write_bytes(installed.read_bytes().replace(b"\r\n", b"\n"))
            contract = deploy.comfy_contract(root, comfy)
            expected = deploy.read_json(root / deploy.SOURCE_MANIFEST)["copies"][0]["sha256"]
            self.assertEqual(contract["files"]["comfy_extras/nodes_wan.py"], expected)

    def test_rollback_refuses_to_remove_a_modified_node(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            deploy.deploy(root, comfy)
            target = comfy / "custom_nodes/fid1_wan_roi_anchor/__init__.py"
            target.write_text(target.read_text(encoding="utf-8") + "\n# owner edit\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed|modified|hash"):
                deploy.rollback(root, comfy)
            self.assertIn("owner edit", target.read_text(encoding="utf-8"))

    def test_rollback_rejects_a_junction_at_the_owned_plugin_directory(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            deploy.deploy(root, comfy)
            plugin = comfy / "custom_nodes/fid1_wan_roi_anchor"
            installed = plugin / "__init__.py"
            with patch.object(deploy, "is_junction", side_effect=lambda path: path == plugin):
                with self.assertRaisesRegex(ValueError, "junction"):
                    deploy.rollback(root, comfy)
            self.assertTrue(installed.is_file())

    def test_rollback_rejects_a_junction_at_the_bytecode_cache(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            deploy.deploy(root, comfy)
            plugin = comfy / "custom_nodes/fid1_wan_roi_anchor"
            cache = plugin / "__pycache__"
            cache.mkdir()
            (cache / "__init__.cpython-312.pyc").write_bytes(b"owned cache fixture")
            installed = plugin / "__init__.py"
            with patch.object(deploy, "is_junction", side_effect=lambda path: path == cache):
                with self.assertRaisesRegex(ValueError, "junction"):
                    deploy.rollback(root, comfy)
            self.assertTrue(installed.is_file())

    def test_junction_detector_falls_back_to_windows_reparse_attributes(self):
        deploy = self.module()
        with patch.object(deploy.Path, "is_junction", None), patch.object(
            deploy.Path, "lstat", return_value=SimpleNamespace(st_file_attributes=0x400)
        ):
            self.assertTrue(deploy.is_junction(Path("fixture")))
        with patch.object(deploy.Path, "is_junction", None), patch.object(
            deploy.Path, "lstat", return_value=SimpleNamespace(st_file_attributes=0)
        ):
            self.assertFalse(deploy.is_junction(Path("fixture")))

    def test_rollback_uses_reparse_fallback_when_path_api_is_unavailable(self):
        deploy = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            shutil.copytree(ROOT / "scripts", root / "scripts")
            shutil.copytree(ROOT / "docs/reviews/20261011-source-fidelity/installed_comfy_source", root / "docs/reviews/20261011-source-fidelity/installed_comfy_source")
            comfy = make_comfy_root(Path(tmp))
            deploy.deploy(root, comfy)
            plugin = comfy / "custom_nodes/fid1_wan_roi_anchor"
            installed = plugin / "__init__.py"
            original_lstat = deploy.Path.lstat

            def fake_lstat(path, *args, **kwargs):
                info = original_lstat(path, *args, **kwargs)
                if path == plugin:
                    return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400)
                return info

            with patch.object(deploy.Path, "is_junction", None), patch.object(deploy.Path, "lstat", new=fake_lstat):
                with self.assertRaisesRegex(ValueError, "junction"):
                    deploy.rollback(root, comfy)
            self.assertTrue(installed.is_file())


if __name__ == "__main__":
    unittest.main()
