# V008 工程对账与现场几何阻塞

唯一计划提交：b37edc51236cf0b340401c0141a2e7687f5b394b。

## 保留历史

- V006/schema4/v2：take10 已运行，117.773秒，输出32e93baca62c6a95d63433a526f85dc78fec239f9e8f09b64cd34509a6663435。Jovi人审PENDING，本地观察仍有头部固定/叠影与背景退化。
- V007/schema5/v3：独立时间权重，保留CPU实现与冻结take11–13；没有部署或GPU，不重封旧job。
- V008/schema6/v4：独立逐ROI强度节点，不含时间权重，不复用旧身份。与V006相比改变强度并新增背景区，属于综合候选，不能做单变量因果归因。
- take09是Jovi真实CHANGES_REQUIRED；服装PASS。SH901/902继续BLOCKED，原30镜审批保持。

## 实际源图几何检查：GEOMETRY_BLOCKED

批准PNG REFB02_01.png，941×1672，SHA6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f。ROI_overlay.png使用该原图直接标注，不生成替代人物或素材。

预注册BACKGROUND_TREES框[.39,.18,.64,.30]明显穿过悟空头冠长翎，框内不能全部作为静态树木处理；还存在疑似水雾区域。强度保护可能压制服饰动态，因此按合同1.1停止该具体候选。没有擅自改框、换图或生成take14，没有将该现场检查当作Jovi审片意见。

latent floor/ceil映射详见ROI_geometry.json；三个盒子无几何交叠，不等于内容语义合格。通用schema6/v4数学、图链、离线fixture准备可以验证，但本机真实take14 prepare/dry-run为NOT_RUN_GEOMETRY_BLOCKED。

现场物理RAM约1GiB，低于8GiB硬门槛（具体时点见resource_state.json）；显存与磁盘可用不能代替RAM。新插件未部署，GPU无本阶段授权。三重阻塞独立记录，不自动降低门槛。

## 远端复审要求

审查固定实现SHA的完整新旧工程及同SHA CI；核实旧证据保护、schema身份隔离、真实Tensor数值和失败关闭。随后基于真实叠层判断该候选是否拒收，若需要修订背景区，给出新的版本身份和固定计划，不覆盖V008预注册配置或历史包。不得据工程绿色宣称视觉修好。
