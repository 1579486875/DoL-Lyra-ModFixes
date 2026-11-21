# 已撤下的模组

| 模组 | 撤下轮次 | 原因 |
|---|---|---|
| `QuotedLinkFix_v2.mod.zip`（Quoted Link Fix 2.0.0） | 第 12 轮 | ① 它要修的「带引号的链接目标」不是死链：SugarCube 的 `Wikifier.helpers.evalPassageId` 对不存在的目标会当表达式求值，`"School Boy's Toilets"` 得到合法的 passage 名，原版作者是有意这么写的。② 它的 `findRegex` 以未转义的 `[[` 开头，是字符类，`all:true` 生效后把 4 个厕所事件 passage 里所有「x]」替换成链接，改坏了 `<<if>>` 代码和链接。详见 `docs/第12轮报告.md` 第一节第 3 条 |

保留文件只为备查，**不要再放进 ModLoader**。
