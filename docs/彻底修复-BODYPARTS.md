# 彻底修复：BODYPARTS_CN_NAME 身体部位名不翻译

> 这个问题困扰了好几个版本，本轮彻底定位并解决。

---

## 最终包

```
APK    : E:\TAML\_dol\out\DoL-Lyra-0.5.12.13-CHS-modded.apk
大小   : 175.77 MB
SHA256 : 1568043897140111BA4A3FF97BB73CEE0BB4B13CD2D1AEF315092447BBBA1A64
```

---

## 根因（三层叠加，最后一层才是真凶）

### 第一层：index 里有两个定义

- `st.BODYPARTS_CN_NAME = mk({...})` —— 47 键，含 penis
- `st.BODYPARTS_CN_NAME = function (x) { var __PB = {...}; }` —— 67 键，含 penis

两者都有 penis，CDP 实测却返回 `"penis"`。

### 第二层：`<<script>>` 块有缓存守卫

```js
if (st.__cnTablesInstalled) return;
st.__cnTablesInstalled = true;
```

### 第三层（真凶）：`Npc Name CN` 模组强制接管

`npcNameCN.js`（v1.3.1）里：

```js
var BODYPARTS = {
    "leftArm": "左臂", ..., "wing": "翅膀", "horn": "角"
};   // ← 只有 30 个键，没有 penis/vagina/anus/breasts/tongue/buttocks

function partCN(v) { return tr(BODYPARTS, v); }

function forceSetup() {
    var st = window.SugarCube.setup;
    // 强制接管：不判断是否已存在
    st.NPC_CN_NAME = nameCN;
    st.NPC_CN_TYPE = typeCN;
    st.NPC_CN_TITLE = titleCN;
    st.BODYPARTS_CN_NAME = partCN;   // ← 无条件覆盖
}
```

**模组最后执行，无条件覆盖所有前面的定义。**
它的表里没有性器官，所以 `partCN("penis")` 返回 `"penis"`。

---

## 解决方案

**改模组本身** —— 补全它自己的 `BODYPARTS` 表：

```js
// 30 键 -> 76 键
var BODYPARTS = {
    ...原有 30 个,
    "penis": "肉棒", "vagina": "阴部", "anus": "肛门",
    "breasts": "胸部", "breast": "胸部", "nipple": "乳头",
    "tongue": "舌头", "buttocks": "臀部", "bottom": "臀部",
    "wings": "翅膀", "horns": "角", "ears": "耳朵",
    "tentacle": "触手", "balls": "睾丸", "pussy": "小穴",
    ...共 46 个新增
};
```

实现：`H06_fix_mod.py` —— 解 base64 模组 zip，改 `npcNameCN.js`，重新编码塞回。
已加入 `build_all`（TF01 之前），每次构建自动执行。

---

## CDP 实测结果

| 函数 | 修复前 | 修复后 |
|---|---|---|
| NPC_CN_TYPE | 40/40 | **40/40** |
| NPC_CN_NAME | 20/20 | **20/20** |
| **BODYPARTS_CN_NAME** | **8/15** | **15/15** |
| description_CN | 10/10 | **10/10** |

具体：
```
penis    -> 肉棒    vagina  -> 阴部    anus    -> 肛门
breasts  -> 胸部    tongue  -> 舌头    buttocks-> 臀部
wings    -> 翅膀
```

---

## 教训

**排查顺序应该是：模组 > index > 记忆印象。**

我之前一直在 index 里找定义、改定义、加定义，
但真正的覆盖来自**最后执行的模组**。

正确做法：
1. **CDP 打印 `setup.XXX.toString()`** —— 一眼看出运行时是哪个版本
2. 按函数名/特征去**模组 zip** 里搜
3. 改模组本身，而不是在 index 里跟它对抗
