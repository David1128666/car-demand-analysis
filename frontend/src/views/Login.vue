<template>
  <div class="login-wrapper" ref="wrapper">
    <canvas ref="bgCanvas" class="bg-canvas"></canvas>
    <div class="login-container">
      <!-- Left: Brand Panel -->
      <div class="brand-panel">
        <div class="brand-inner">
          <div class="car-graphic">
            <svg viewBox="0 0 320 180" fill="none" xmlns="http://www.w3.org/2000/svg" class="car-svg">
              <defs>
                <linearGradient id="carBody" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#a78bfa"/>
                  <stop offset="40%" stop-color="#818cf8"/>
                  <stop offset="100%" stop-color="#60a5fa"/>
                </linearGradient>
                <linearGradient id="carGlass" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#c9a96e" stop-opacity="0.55"/>
                  <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.25"/>
                </linearGradient>
                <linearGradient id="carAccent" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#c9a96e"/>
                  <stop offset="50%" stop-color="#a78bfa"/>
                  <stop offset="100%" stop-color="#60a5fa"/>
                </linearGradient>
                <filter id="carGlow">
                  <feGaussianBlur stdDeviation="2.5" result="blur"/>
                  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
              </defs>
              <!-- Ground reflection -->
              <ellipse cx="165" cy="148" rx="120" ry="5" fill="url(#carBody)" opacity="0.12"/>
              <line x1="30" y1="142" x2="300" y2="142" stroke="url(#carAccent)" stroke-width="0.4" opacity="0.25"/>
              <!-- Spoiler -->
              <path d="M240 52 L275 50 L278 55 L245 57Z" fill="url(#carBody)" opacity="0.7" filter="url(#carGlow)"/>
              <!-- Car body upper -->
              <path d="M42 120 L32 120 L48 68 L78 48 L115 38 L175 34 L228 40 L262 52 L285 68 L295 85 L298 105 L298 120 L285 120 L280 108 L275 65 L240 55 L180 46 L120 48 L80 56 L55 78 L48 110 L42 120Z" fill="url(#carBody)" filter="url(#carGlow)"/>
              <!-- Side intake -->
              <path d="M195 65 L230 62 L235 80 L200 82Z" fill="url(#carBody)" opacity="0.5"/>
              <!-- Window -->
              <path d="M115 45 L148 39 L200 42 L230 52 L235 72 L218 78 L148 76 L120 68 L112 58Z" fill="url(#carGlass)" stroke="url(#carAccent)" stroke-width="0.6"/>
              <!-- Window divider -->
              <line x1="160" y1="42" x2="160" y2="76" stroke="url(#carAccent)" stroke-width="0.4" opacity="0.5"/>
              <!-- Front wheel -->
              <circle cx="255" cy="130" r="18" stroke="url(#carAccent)" stroke-width="2.2" fill="none" opacity="0.8"/>
              <circle cx="255" cy="130" r="10" stroke="url(#carAccent)" stroke-width="1.2" fill="none" opacity="0.5"/>
              <circle cx="255" cy="130" r="4" fill="url(#carAccent)" opacity="0.7"/>
              <!-- Rear wheel -->
              <circle cx="90" cy="130" r="18" stroke="url(#carAccent)" stroke-width="2.2" fill="none" opacity="0.8"/>
              <circle cx="90" cy="130" r="10" stroke="url(#carAccent)" stroke-width="1.2" fill="none" opacity="0.5"/>
              <circle cx="90" cy="130" r="4" fill="url(#carAccent)" opacity="0.7"/>
              <!-- Headlight -->
              <ellipse cx="296" cy="98" rx="4" ry="7" fill="#fef3c7" opacity="0.9" filter="url(#carGlow)"/>
              <!-- Taillight -->
              <ellipse cx="34" cy="98" rx="3" ry="5" fill="#ef4444" opacity="0.8"/>
              <!-- Lower body line -->
              <path d="M48 110 L285 108" stroke="url(#carAccent)" stroke-width="0.3" opacity="0.4"/>
              <!-- Speed lines -->
              <line x1="58" y1="82" x2="78" y2="82" stroke="url(#carAccent)" stroke-width="0.4" opacity="0.25"/>
              <line x1="50" y1="88" x2="65" y2="88" stroke="url(#carAccent)" stroke-width="0.3" opacity="0.2"/>
            </svg>
          </div>
          <div class="brand-text">
            <h1 class="project-title">基于多源行为数据的汽车需求挖掘与推荐系统</h1>
            <div class="welcome-badge">WELCOME</div>
          </div>
        </div>
      </div>

      <!-- Right: Form Panel -->
      <div class="form-panel">
        <div class="form-inner">
          <template v-if="!showReg">
            <h2 class="form-title">用户登录</h2>
            <p class="form-subtitle">登录以访问汽车需求分析平台</p>
            <input
              v-model="form.username"
              placeholder="请输入用户名"
              class="form-input"
              @keyup.enter="doLogin"
              autocomplete="username"
            />
            <input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              class="form-input"
              @keyup.enter="doLogin"
              autocomplete="current-password"
            />
            <div v-if="msg" class="form-msg" :class="msgOk ? 'msg-success' : 'msg-error'">{{ msg }}</div>
            <button type="button" class="form-btn" @click="doLogin" :disabled="busy">
              <span v-if="busy" class="btn-spinner"></span>
              {{ busy ? '登录中...' : '登 录' }}
            </button>
            <p class="switch-tip">还没有账号？<a href="#" @click.prevent="switchToReg">立即注册</a></p>
          </template>

          <template v-else>
            <h2 class="form-title">账号注册</h2>
            <p class="form-subtitle">创建账号以使用完整功能</p>
            <input v-model="form.username" placeholder="请输入用户名" class="form-input" />
            <input v-model="form.nickname" placeholder="请输入昵称" class="form-input" />
            <input
              v-model="form.password"
              type="password"
              placeholder="请输入密码（至少6位字母或数字）"
              class="form-input"
            />
            <div v-if="msg" class="form-msg" :class="msgOk ? 'msg-success' : 'msg-error'">{{ msg }}</div>
            <button type="button" class="form-btn" @click="doReg" :disabled="busy">
              <span v-if="busy" class="btn-spinner"></span>
              {{ busy ? '注册中...' : '注 册' }}
            </button>
            <p class="switch-tip">已有账号？<a href="#" @click.prevent="switchToLogin">返回登录</a></p>
          </template>
        </div>
      </div>
    </div>
    <p class="demo-hint">演示账号：admin / admin123</p>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const form = reactive({ username: "", password: "", nickname: "" });
const msg = ref("");
const msgOk = ref(false);
const busy = ref(false);
const showReg = ref(false);

function switchToReg() {
  form.password = "";
  msg.value = "";
  showReg.value = true;
}

function switchToLogin() {
  form.password = "";
  msg.value = "";
  showReg.value = false;
}

async function doLogin() {
  if (!form.username || !form.password) {
    msg.value = "请输入用户名和密码";
    msgOk.value = false;
    return;
  }
  busy.value = true;
  msg.value = "";
  try {
    const result = await auth.login(form.username, form.password);
    if (result.success) {
      router.push("/");
    } else {
      msg.value = result.message || "用户名或密码错误";
      msgOk.value = false;
    }
  } catch (e) {
    console.error(e);
    msg.value = e.message || "登录失败，请检查后端服务是否开启";
    msgOk.value = false;
  }
  busy.value = false;
}

async function doReg() {
  if (!form.username || !form.password) {
    msg.value = "用户名和密码不能为空";
    msgOk.value = false;
    return;
  }
  if (form.password.length < 6) {
    msg.value = "密码长度不能少于6位字母或数字";
    msgOk.value = false;
    return;
  }
  if (!/^[a-zA-Z0-9]+$/.test(form.password)) {
    msg.value = "密码只能包含字母和数字";
    msgOk.value = false;
    return;
  }
  busy.value = true;
  msg.value = "";
  try {
    const res = await auth.register(form.username, form.password, form.nickname);
    if (res.code === 200 && res.data?.success) {
      showReg.value = false;
      msg.value = "注册成功，请登录";
      msgOk.value = true;
    } else {
      msg.value = res.data?.message || "注册失败，请重试";
      msgOk.value = false;
    }
  } catch (e) {
    console.error(e);
    msg.value = e.message || "注册失败，请检查后端服务是否开启";
    msgOk.value = false;
  }
  busy.value = false;
}

// Particle network background
const wrapper = ref(null);
const bgCanvas = ref(null);
let animId = null;

onMounted(() => {
  const canvas = bgCanvas.value;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const resize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  resize();
  window.addEventListener("resize", resize);

  const count = 120;
  const pts = [];
  let mx = -999, my = -999;

  for (let i = 0; i < count; i++) {
    pts.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      r: Math.random() * 2.0 + 0.8,
      baseR: 0,
      hue: i % 2,
    });
    pts[i].baseR = pts[i].r;
  }

  const wrap = wrapper.value;
  if (wrap) {
    wrap.addEventListener("mousemove", (e) => {
      mx = e.clientX;
      my = e.clientY;
    });
    wrap.addEventListener("mouseleave", () => {
      mx = -999;
      my = -999;
    });
  }

  const draw = () => {
    const fadeSpeed = 0.35;
    ctx.fillStyle = `rgba(10,14,23,${fadeSpeed})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < count; i++) {
      const p = pts[i];
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < -20) p.x = canvas.width + 20;
      if (p.x > canvas.width + 20) p.x = -20;
      if (p.y < -20) p.y = canvas.height + 20;
      if (p.y > canvas.height + 20) p.y = -20;

      const dxm = mx - p.x, dym = my - p.y;
      const dm = Math.sqrt(dxm * dxm + dym * dym);
      if (dm < 200 && dm > 0) {
        p.vx += (dxm / dm) * 0.03;
        p.vy += (dym / dm) * 0.03;
        p.r = p.baseR * 1.6;
      } else {
        p.r += (p.baseR - p.r) * 0.08;
      }
      p.vx *= 0.998;
      p.vy *= 0.998;
      const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
      if (speed < 0.15) { p.vx *= 1.02; p.vy *= 1.02; }

      const isPurple = p.hue > 0;
      const glowR = isPurple ? 139 : 59;
      const glowG = isPurple ? 92 : 130;
      const glowB = isPurple ? 246 : 246;
      const glow = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 3.5);
      glow.addColorStop(0, `rgba(${glowR},${glowG},${glowB},0.5)`);
      glow.addColorStop(0.4, `rgba(${glowR},${glowG},${glowB},0.12)`);
      glow.addColorStop(1, `rgba(${glowR},${glowG},${glowB},0)`);
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * 3.5, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = isPurple ? "rgba(190,170,255,0.85)" : "rgba(139,190,255,0.85)";
      ctx.fill();

      for (let j = i + 1; j < count; j++) {
        const q = pts[j];
        const dx = p.x - q.x, dy = p.y - q.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 140) {
          const alpha = 0.11 * (1 - dist / 140);
          const connColor = (isPurple || pts[j].hue > 0) ? `rgba(150,140,240,${alpha})` : `rgba(100,160,255,${alpha})`;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(q.x, q.y);
          ctx.strokeStyle = connColor;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    animId = requestAnimationFrame(draw);
  };
  draw();
});

onUnmounted(() => {
  if (animId) cancelAnimationFrame(animId);
});
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  width: 100vw;
  position: relative;
  overflow: hidden;
  background: var(--bg-primary);
}

.login-wrapper::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  opacity: 0.4;
  background:
    radial-gradient(ellipse at 25% 45%, rgba(139,92,246,0.14) 0%, transparent 60%),
    radial-gradient(ellipse at 70% 25%, rgba(99,102,241,0.10) 0%, transparent 55%),
    radial-gradient(ellipse at 55% 75%, rgba(59,130,246,0.10) 0%, transparent 55%),
    radial-gradient(ellipse at 40% 60%, rgba(168,85,247,0.06) 0%, transparent 70%);
  animation: bgShift 10s ease-in-out infinite alternate;
}

@keyframes bgShift {
  0%   { opacity: 0.30; transform: scale(1); }
  100% { opacity: 0.50; transform: scale(1.06); }
}

.bg-canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

/* ---- Two-card container ---- */
.login-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  display: flex;
  gap: 0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow:
    0 0 60px rgba(139,92,246,0.10),
    0 0 120px rgba(59,130,246,0.05),
    0 0 200px rgba(99,102,241,0.03);
}

/* ---- Rotating border glow ---- */
.login-container::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 18px;
  z-index: -1;
  background: conic-gradient(from 0deg, transparent, rgba(139,92,246,0.35), rgba(59,130,246,0.30), transparent, rgba(168,85,247,0.25), transparent);
  animation: rotateBorder 8s linear infinite;
  opacity: 0.55;
  filter: blur(10px);
}

.login-container::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 17px;
  z-index: -1;
  background: conic-gradient(from 120deg, transparent, rgba(99,102,241,0.3), transparent, rgba(139,92,246,0.25), transparent, rgba(59,130,246,0.25));
  animation: rotateBorder 10s linear infinite reverse;
  opacity: 0.35;
}

@keyframes rotateBorder {
  to { transform: rotate(360deg); }
}

/* ---- Brand Panel (Left) ---- */
.brand-panel {
  width: 380px;
  background: linear-gradient(180deg, rgba(17,24,39,0.95) 0%, rgba(26,31,46,0.95) 50%, rgba(17,24,39,0.95) 100%);
  border-right: 1px solid rgba(139,92,246,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* Subtle geometric decoration */
.brand-panel::before {
  content: '';
  position: absolute;
  top: -60px;
  right: -60px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
}

.brand-panel::after {
  content: '';
  position: absolute;
  bottom: -40px;
  left: -40px;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(201,169,110,0.06) 0%, transparent 70%);
}

.brand-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 32px;
  text-align: center;
}

.car-graphic {
  margin-bottom: 28px;
  animation: carFloat 4s ease-in-out infinite;
}

@keyframes carFloat {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-8px); }
}

.car-svg {
  width: 260px;
  height: auto;
  filter: drop-shadow(0 8px 24px rgba(139,92,246,0.2));
}

.project-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.7;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #e2e8f0 0%, var(--accent) 40%, var(--purple) 70%, var(--luxury) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
}

.welcome-badge {
  display: inline-block;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 8px;
  background: linear-gradient(135deg, var(--luxury), #e2c682);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
}

.welcome-badge::after {
  content: '';
  display: block;
  width: 60%;
  height: 1px;
  margin: 8px auto 0;
  background: linear-gradient(90deg, transparent, var(--luxury), transparent);
  opacity: 0.5;
}

/* ---- Form Panel (Right) ---- */
.form-panel {
  width: 400px;
  background: rgba(17,24,39,0.9);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-inner {
  width: 100%;
  padding: 44px 40px;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.form-subtitle {
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 24px;
}

.form-input {
  width: 100%;
  padding: 11px 14px;
  margin-bottom: 12px;
  background: rgba(26,31,46,0.7);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  transition: border-color 0.3s, box-shadow 0.3s;
  outline: none;
}

.form-input:focus {
  border-color: var(--purple);
  box-shadow: 0 0 0 3px rgba(139,92,246,0.12);
}

.form-input::placeholder {
  color: rgba(148,163,184,0.5);
}

.form-msg {
  font-size: 12px;
  margin-bottom: 10px;
  padding: 6px 10px;
  border-radius: 6px;
  animation: fadeSlideIn 0.25s ease-out;
}

.msg-error {
  color: var(--danger);
  background: rgba(239,68,68,0.08);
  border: 1px solid rgba(239,68,68,0.2);
}

.msg-success {
  color: var(--success);
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.2);
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}

.form-btn {
  width: 100%;
  padding: 11px;
  margin-top: 4px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, var(--accent), var(--purple));
  transition: all 0.25s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  user-select: none;
  -webkit-user-select: none;
}

.form-btn:hover:not(:disabled) {
  box-shadow: 0 0 20px var(--purple-glow);
  transform: translateY(-1px);
}

.form-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.form-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.switch-tip {
  text-align: center;
  margin-top: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

.switch-tip a {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.switch-tip a:hover {
  color: var(--purple);
}

.demo-hint {
  position: absolute;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  font-size: 11px;
  color: var(--text-secondary);
  opacity: 0.6;
  white-space: nowrap;
}

/* ---- Responsive ---- */
@media (max-width: 820px) {
  .login-container {
    flex-direction: column;
    width: 90%;
    max-width: 400px;
  }
  .brand-panel {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid rgba(139,92,246,0.15);
  }
  .brand-inner { padding: 28px 24px; }
  .car-svg { width: 180px; }
  .project-title { font-size: 13px; }
  .welcome-badge { font-size: 22px; letter-spacing: 6px; }
  .form-panel { width: 100%; }
  .form-inner { padding: 28px 24px; }
}
</style>
