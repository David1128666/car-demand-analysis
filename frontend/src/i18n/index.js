import { computed, ref } from "vue";

import en from "../locales/en";
import zhCN from "../locales/zh-CN";

const messages = {
  en,
  "zh-CN": zhCN,
};

const storageKey = "car-demand-locale";
const environmentLocale = import.meta.env.VITE_APP_LANGUAGE || "en";
const storedLocale =
  typeof window !== "undefined" ? window.localStorage.getItem(storageKey) : null;

export const locale = ref(
  messages[storedLocale] ? storedLocale : environmentLocale,
);

export const localeLabel = computed(() =>
  locale.value === "en" ? "中文" : "EN",
);

export function t(key, params = {}) {
  const dictionary = messages[locale.value] || messages.en;
  const template = dictionary[key] || messages.en[key] || key;
  return template.replace(/\{(\w+)\}/g, (_, name) =>
    params[name] === null || params[name] === undefined
      ? ""
      : String(params[name]),
  );
}

export function setLocale(nextLocale) {
  if (!messages[nextLocale]) {
    return;
  }
  locale.value = nextLocale;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(storageKey, nextLocale);
    document.documentElement.lang = nextLocale;
    document.title = t("app.title");
  }
}

export function toggleLocale() {
  setLocale(locale.value === "en" ? "zh-CN" : "en");
}

const enumKeys = {
  "轿车": "enum.carType.sedan",
  "皮卡": "enum.carType.pickup",
  "猎装车": "enum.carType.shootingBrake",
  "跑车": "enum.carType.sports",
  "新能源": "enum.carType.newEnergy",
  "纯电动": "enum.fuel.bev",
  "纯电": "enum.fuel.bev",
  "混合动力": "enum.fuel.hybrid",
  "混动": "enum.fuel.hybrid",
  "插电混动": "enum.fuel.phev",
  "增程": "enum.fuel.erev",
  "增程式": "enum.fuel.erev",
  "汽油": "enum.fuel.gasoline",
  "柴油": "enum.fuel.diesel",
  "氢能": "enum.fuel.hydrogen",
  "协同过滤": "enum.rec.collaborative",
  collaborative: "enum.rec.collaborative",
  content_based: "enum.rec.contentBased",
  hot: "enum.rec.hot",
  hybrid: "enum.rec.hybrid",
  "商业贷款": "enum.loan.commercial",
  "信用卡分期": "enum.loan.creditInstallment",
  "汽车金融": "enum.loan.autoFinance",
  "银行直贷": "enum.loan.bankLoan",
  "融资租赁": "enum.loan.leasing",
  "官降": "enum.priceReason.officialCut",
  "促销活动": "enum.priceReason.promotion",
  "限时优惠": "enum.priceReason.limitedOffer",
  "置换补贴": "enum.priceReason.tradeInSubsidy",
  "金融优惠": "enum.priceReason.financeOffer",
  "节日特惠": "enum.priceReason.holiday",
  "库存清仓": "enum.priceReason.inventoryClearance",
  "超高折扣(≥96%)": "enum.discount.ultraHigh",
  "高折扣(93-96%)": "enum.discount.high",
  "中高折扣(90-93%)": "enum.discount.mediumHigh",
  "中折扣(87-90%)": "enum.discount.medium",
  "普通折扣(<87%)": "enum.discount.regular",
};

export function valueLabel(value) {
  const key = enumKeys[value];
  return key ? t(key) : value;
}

export function promotionLabel(value) {
  if (!value) return "";
  let match = value.match(/^限时优惠(\d+)万元$/);
  if (match) return t("promotion.limitedOffer", { amount: match[1] });
  match = value.match(/^送(\d+)年保养$/);
  if (match) return t("promotion.maintenance", { years: match[1] });
  match = value.match(/^金融贴息(\d+)千元$/);
  if (match) return t("promotion.financeSubsidy", { amount: match[1] });
  if (value === "免购置税") return t("promotion.taxFree");
  return value;
}

const backendMessageKeys = {
  "用户名已存在": "error.usernameExists",
  "用户名或密码错误": "error.invalidCredentials",
  "账号已被禁用": "error.accountDisabled",
  "仅管理员可操作": "error.adminOnly",
  "仅管理员可查看用户列表": "error.adminOnly",
  "不能删除自己": "error.cannotDeleteSelf",
  "车辆不存在": "error.carNotFound",
};

export function apiMessage(message, fallbackKey = "error.requestFailed") {
  const key = backendMessageKeys[message];
  return key ? t(key) : t(fallbackKey);
}

if (typeof window !== "undefined") {
  window.localStorage.setItem(storageKey, locale.value);
  document.documentElement.lang = locale.value;
  document.title = t("app.title");
}
