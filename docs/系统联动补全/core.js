/*
 * 系统联动补全 · 核心逻辑
 *
 * 设计原则：
 *   1. 只读取现有状态，只追加副作用（$stress / $trauma / $fame / $tiredness）
 *   2. 绝不修改 $exposed、战斗公式、渲染层
 *   3. 每个联动独立开关 + 冷却，出错时静默跳过，绝不让游戏崩
 *   4. 所有状态存 V.联动，带 version，升级自动迁移
 */
(function () {
	'use strict';

	/* ============ 基础设施 ============ */

	var LOG_PREFIX = '[联动]';
	var VERSION = 1;

	function log() {
		if (!V.联动 || !V.联动.debug) return;
		try { console.log.apply(console, [LOG_PREFIX].concat([].slice.call(arguments))); } catch (e) {}
	}

	/** 安全读取：任何一层 undefined 都返回 fallback */
	function safe(fn, fallback) {
		try { var v = fn(); return (v === undefined || v === null) ? fallback : v; } catch (e) { return fallback; }
	}

	/** 取上限，缺省给合理值 */
	function cap(name, dflt) {
		return safe(function () { return V[name]; }, dflt) || dflt;
	}

	/** 加压力（自动 clamp） */
	function addStress(n) {
		try {
			if (typeof n !== 'number' || !isFinite(n) || n === 0) return;
			var max = cap('stressmax', 10000);
			V.stress = Math.max(0, Math.min(max, (V.stress || 0) + n));
		} catch (e) {}
	}

	/** 加创伤（自动 clamp） */
	function addTrauma(n) {
		try {
			if (typeof n !== 'number' || !isFinite(n) || n === 0) return;
			var max = cap('traumamax', 5000);
			V.trauma = Math.max(0, Math.min(max, (V.trauma || 0) + n));
		} catch (e) {}
	}

	/** 加暴露名声（自动 clamp 到 2000，沿用原版写法） */
	function addFame(n) {
		try {
			if (typeof n !== 'number' || !isFinite(n) || n === 0) return;
			if (!V.fame) V.fame = {};
			V.fame.exhibitionism = Math.max(0, Math.min(2000, (V.fame.exhibitionism || 0) + n));
		} catch (e) {}
	}

	/** 加性奋（原版上限 $arousalmax，缺省 1000） */
	function addArousal(n) {
		try {
			if (typeof n !== 'number' || !isFinite(n) || n === 0) return;
			var max = cap('arousalmax', 1000);
			V.arousal = Math.max(0, Math.min(max, (V.arousal || 0) + n));
		} catch (e) {}
	}

	/** 加疲劳 */
	function addTiredness(n) {
		try {
			if (typeof n !== 'number' || !isFinite(n) || n === 0) return;
			var max = cap('tirednessmax', 10000);
			V.tiredness = Math.max(0, Math.min(max, (V.tiredness || 0) + n));
		} catch (e) {}
	}

	/* ============ 状态 ============ */

	function ensureState() {
		if (!V.联动) {
			V.联动 = {
				version: VERSION,
				debug: false,
				on: { accident: true, tear: true, battle: true, photo: true, home: true },
				cool: {},
				lastBladder: null,
				lastBladderFull: 0,
				lastPhoto: null,
				lastCombat: false,
				homeNude: false
			};
			return;
		}
		// 版本迁移
		if (V.联动.version !== VERSION) {
			V.联动.version = VERSION;
			if (!V.联动.on) V.联动.on = { accident: true, tear: true, battle: true, photo: true, home: true };
			if (!V.联动.cool) V.联动.cool = {};
		}
		// 兜底缺字段
		if (!V.联动.on) V.联动.on = { accident: true, tear: true, battle: true, photo: true, home: true };
		if (!V.联动.cool) V.联动.cool = {};
	}

	/** 冷却：同一联动 key 在 ms 内只触发一次 */
	function cooling(key, ms) {
		try {
			var now = Date.now();
			var last = V.联动.cool[key] || 0;
			if (now - last < ms) return true;
			V.联动.cool[key] = now;
			return false;
		} catch (e) { return true; }
	}

	function enabled(key) {
		return safe(function () { return V.联动.on[key] !== false; }, true);
	}

	/* ============ 环境判定 ============ */

	/** 取当前 passage（State.passage 最可靠，V.passage 兜底） */
	function currentPassage() {
		var p = safe(function () { return State.passage; }, '');
		if (p) return p;
		return safe(function () { return V.passage; }, '');
	}

	/** 是否在解手场景（主动去厕所，不是失禁） */
	var RELIEF_RE = /bathroom|toilet|bath\b|shower|latrine|washroom|spa\b|pisser/i;
	function inReliefScene() {
		return RELIEF_RE.test(currentPassage());
	}

	/** 是否在自家房产（maplebirch 的 realEstate.current 或 passage 名） */
	function inOwnHome() {
		var cur = safe(function () {
			return maplebirch && maplebirch.get && maplebirch.get('Finance').realEstate.current;
		}, null);
		if (cur) return true;
		return /Deadwood Reblooms|Flats Own|Cottage|Manor|Estate/i.test(currentPassage());
	}

	/** 当前是否公共场合（有暴露判定或在外） */
	var PUBLIC_RE = /street|alley|park|road|high street|shopping|market|beach|lake|forest|farm|school|shop|cafe|pub|club|brothel|prison/i;
	function inPublic() {
		if (PUBLIC_RE.test(currentPassage())) return true;
		// 暴露状态 1/2 也是公共信号
		return safe(function () { return V.exposed; }, 0) >= 1;
	}

	/** 是否介意裸体 */
	function ashamedOfNude() {
		return safe(function () { return V.uncomfortable && V.uncomfortable.nude === true; }, false);
	}

	/* ============ 联动 1：失禁 → 羞耻 / 名声 ============ */

	function onAccident() {
		if (!enabled('accident')) return;
		if (cooling('accident', 10 * 60 * 1000)) return;

		var pub = inPublic();
		var ashamed = ashamedOfNude();
		var home = inOwnHome();

		if (home) {
			// 在家：只有轻微难堪
			addStress(150);
			ShowBanner('accident_home');
			log('失禁·在家');
			return;
		}

		if (!pub) {
			// 无人：轻压力
			addStress(300);
			ShowBanner('accident_private');
			log('失禁·私密');
			return;
		}

		if (ashamed) {
			// 公共 + 羞耻
			addStress(1800);
			addTrauma(120);
			addFame(5);
			ShowBanner('accident_public_ashamed');
			log('失禁·公共·羞耻');
		} else {
			// 公共 + 不在意
			addStress(700);
			addFame(2);
			addArousal(40);
			ShowBanner('accident_public_shameless');
			log('失禁·公共·不在意');
		}
	}

	/* ============ 联动 2：服装破损 → 走光 ============ */

	var TEAR_SLOTS = ['upper', 'lower', 'under_upper', 'under_lower'];
	var TEAR_NAMES = { upper: '上衣', lower: '下装', under_upper: '内衣', under_lower: '内裤' };

	function onTearCheck() {
		if (!enabled('tear')) return;
		var worn = safe(function () { return V.worn; }, null);
		if (!worn) return;

		var worst = null;   // 最严重的槽位
		var worstRatio = 1;

		for (var i = 0; i < TEAR_SLOTS.length; i++) {
			var slot = TEAR_SLOTS[i];
			var item = safe(function () { return worn[slot]; }, null);
			if (!item) continue;
			// 裸体状态跳过
			if (safe(function () { return item.name; }, '') === 'naked') continue;
			var max = safe(function () { return item.integrity_max; }, 0) || 0;
			if (max <= 0) continue;
			var cur = safe(function () { return item.integrity; }, max) || 0;
			var ratio = cur / max;
			if (ratio < worstRatio) {
				worstRatio = ratio;
				worst = slot;
			}
		}

		if (!worst) return;

		if (worstRatio < 0.35) {
			// 走光
			if (cooling('tear_' + worst, 5 * 60 * 1000)) return;
			addStress(60);
			addFame(1);
			ShowBanner('tear_broken');
			log('走光', worst, worstRatio.toFixed(2));
		} else if (worstRatio < 0.7) {
			// 半透
			if (cooling('tear_thin_' + worst, 5 * 60 * 1000)) return;
			addStress(20);
			ShowBanner('tear_thin');
			log('半透', worst, worstRatio.toFixed(2));
		}
	}

	/* ============ 联动 3：需求 → 战斗表现 ============ */

	/**
	 * 战斗不是独立 passage，靠 $combat 变量切换。
	 * 这里只在"刚开战"那一刻结算一次，不逐回合刷，避免压力膨胀。
	 * 不改任何战斗数值，只加副作用与提示文本。
	 */
	function onBattleStart() {
		if (!enabled('battle')) return;
		var bn = safe(function () { return V.BasicNeeds; }, null);
		if (!bn) return;

		var thirst = safe(function () { return bn.thirst; }, 0) || 0;
		var bladder = safe(function () { return bn.bladder; }, 0) || 0;

		var urgent = [];
		if (thirst >= 8000) urgent.push('thirst');
		if (bladder >= 8000) urgent.push('bladder');
		if (!urgent.length) return;

		if (cooling('battle', 5 * 60 * 1000)) return;

		if (bladder >= 8000) {
			// 尿意最拖累，优先
			addStress(300);
			ShowBanner('battle_bladder');
			log('战斗·尿急');
		} else if (thirst >= 8000) {
			addStress(200);
			ShowBanner('battle_thirst');
			log('战斗·口渴');
		}
	}

	/* ============ 联动 4：拍照 → 暴露名声 ============ */

	/**
	 * 手机每次拍照 V.Phone.photography += 1（上限 1000，每天限 10 次）。
	 * 这里靠它的增长判定"刚拍了照"，再按场合给名声。
	 * 上限 1000 后不再增长，所以不会无限刷。
	 */
	function onPhotoCheck() {
		if (!enabled('photo')) return;
		var cur = safe(function () { return V.Phone && V.Phone.photography; }, null);
		if (cur === null) return;
		var last = V.联动.lastPhoto;
		V.联动.lastPhoto = cur;

		if (last === null || cur <= last) return;   // 没拍照

		if (cooling('photo', 60 * 1000)) return;    // 1 分钟内只算一次

		var exposed = safe(function () { return V.exposed; }, 0) || 0;

		if (exposed >= 1) {
			// 暴露状态下拍 —— 照片本身就是证据
			addFame(5);
			addStress(100);
			addArousal(60);
			ShowBanner('photo_exposed');
			log('拍照·暴露');
		} else if (inPublic()) {
			// 公共场合拍 —— 有点张扬
			addFame(1);
			ShowBanner('photo_public');
			log('拍照·公共');
		}
	}

	/* ============ 联动 5：在自家 → 放松（反向反馈） ============ */

	/**
	 * 原版在自家裸体一样会算暴露名声，这里做一个"安全区"的反向补偿：
	 * 在家且处于暴露状态时，缓慢削减压力。这是正向反馈，不改原版名声，
	 * 避免动到 $fame 引起不可预期的连锁。
	 */
	function onHomeRelief() {
		if (!enabled('home')) return;
		if (!inOwnHome()) return;
		var exposed = safe(function () { return V.exposed; }, 0) || 0;
		if (exposed < 1) return;
		if (cooling('home_relief', 3 * 60 * 1000)) return;

		var stress = safe(function () { return V.stress; }, 0) || 0;
		if (stress <= 0) return;

		// 削减 8%，最多 200，避免一次抹平
		var cut = Math.min(200, Math.max(20, Math.round(stress * 0.08)));
		addStress(-cut);
		ShowBanner('home_relief');
		log('在家放松 -' + cut);
	}

	/* ============ 文本投递 ============ */

	/**
	 * 把文本插到当前 passage 末尾。
	 * 文本用 twee widget 定义（Keyed 到 widget 名），这里只负责调用，
	 * 避免在 JS 里拼长中文字符串，也避免手拼 HTML 出错。
	 */
	function ShowBanner(widgetName) {
		try {
			// 多重兜底：不同 SugarCube 版本的容器结构不一样
			var target = jQuery('#passages .passage').last().find('.passage-content');
			if (!target.length) target = jQuery('#passages .passage').last();
			if (!target.length) target = jQuery('.passage').last().find('.passage-content');
			if (!target.length) target = jQuery('.passage').last();
			if (!target.length) target = jQuery('#passages');
			if (!target.length) { log('找不到插入点'); return; }

			var box = jQuery('<div class="联动文本"></div>');
			target.append(box);

			var code = '<<' + widgetName + '>>';
			if (window.Wikifier) {
				new Wikifier(box[0], code);
			} else if (window.SugarCube && SugarCube.Wikifier && SugarCube.Wikifier.wikifyEval) {
				SugarCube.Wikifier.wikifyEval(box[0], code);
			} else {
				box.text('（文本渲染失败：' + widgetName + '）');
			}
		} catch (e) {
			log('文本投递失败', e && e.message);
		}
	}

	/* ============ 主循环 ============ */

	function tick() {
		try {
			ensureState();

			/* —— 联动 1：失禁检测 ——
			 * accident() 是 BasicNeeds 的闭包内函数，hook 不到。
			 * 改用状态跳变：上一帧 bladder >= 9000，这一帧归 0，且不在解手场景。
			 */
			var bn = safe(function () { return V.BasicNeeds; }, null);
			if (bn) {
				var cur = safe(function () { return bn.bladder; }, 0) || 0;
				var curFull = safe(function () { return bn.bladderFullHrs; }, 0) || 0;
				var last = V.联动.lastBladder;

				if (last !== null && last >= 9000 && cur === 0 && !inReliefScene()) {
					onAccident();
				}
				V.联动.lastBladder = cur;
				V.联动.lastBladderFull = curFull;
			}

			/* —— 联动 2：服装破损 → 走光 —— */
			onTearCheck();

			/* —— 联动 3：需求 → 战斗（只在开战瞬间结算）—— */
			var combatNow = safe(function () { return V.combat; }, false) ? true : false;
			if (combatNow && V.联动.lastCombat !== true) {
				onBattleStart();
			}
			V.联动.lastCombat = combatNow;

			/* —— 联动 4：拍照 → 名声 —— */
			onPhotoCheck();

			/* —— 联动 5：在自家放松 —— */
			onHomeRelief();
		} catch (e) {
			log('tick 异常', e && e.message);
		}
	}

	/* ============ 注册 ============ */

	/**
	 * 延后一帧再检测：BasicNeeds 自己也挂在 :passageend 上，
	 * 它先跑会把 bladder 重算掉，直接读会读不到"归零瞬间"。
	 * setTimeout(0) 保证在它之后执行。
	 */
	$(document).on(':passageend', function () {
		setTimeout(function () {
			try { tick(); } catch (e) { log('tick 异常', e && e.message); }
		}, 0);
	});

	$(document).on(':passagestart', function () {
		// 换场景时重置基线，避免跨场景误判
		try {
			ensureState();
			var bn = safe(function () { return V.BasicNeeds; }, null);
			if (bn) V.联动.lastBladder = safe(function () { return bn.bladder; }, 0) || 0;
			// 摄影值同样归位，避免第一次拍照漏判
			var ph = safe(function () { return V.Phone && V.Phone.photography; }, null);
			if (ph !== null) V.联动.lastPhoto = ph;
			V.联动.lastCombat = safe(function () { return V.combat; }, false) ? true : false;
		} catch (e) {}
	});

	window.系统联动 = {
		version: VERSION,
		onAccident: onAccident,
		tick: tick
	};

	log('已加载 v' + VERSION);
})();
