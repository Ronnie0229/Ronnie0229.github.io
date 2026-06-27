import { cleanMarkdown } from "./text";

export interface TopicInput {
  title?: string;
  description?: string;
  scripture?: string;
  tags?: string[];
  body?: string;
}

export interface KnowledgeTopic {
  id: string;
  zh: string;
  en: string;
  aliases: string[];
  description: string;
}

export const KNOWLEDGE_TOPICS: KnowledgeTopic[] = [
  {
    id: "grace",
    zh: "恩典",
    en: "Grace",
    aliases: ["恩典", "白白", "礼物", "赏赐", "怜悯", "慈爱", "够用的恩典"],
    description: "关于神主动赐下救恩、怜悯和供应的文章。"
  },
  {
    id: "faith",
    zh: "信心",
    en: "Faith",
    aliases: ["信心", "相信", "信靠", "倚靠", "信实", "不信", "真正得救"],
    description: "关于信靠神、真实信仰和信心操练的文章。"
  },
  {
    id: "repentance",
    zh: "悔改",
    en: "Repentance",
    aliases: ["悔改", "回转", "认罪", "蒙赦免", "赦免", "省察", "不要再犯罪"],
    description: "关于认罪、回转归向神和生命更新的文章。"
  },
  {
    id: "hope",
    zh: "盼望",
    en: "Hope",
    aliases: ["盼望", "等候", "忍耐", "安慰", "荣耀", "永恒", "复活的盼望"],
    description: "关于在基督里等候、忍耐并面向永恒的文章。"
  },
  {
    id: "love",
    zh: "爱",
    en: "Love",
    aliases: ["爱", "相爱", "彼此相爱", "爱心", "慈爱", "和睦", "祝福", "接纳"],
    description: "关于爱神、爱人、彼此相爱和关系修复的文章。"
  },
  {
    id: "church",
    zh: "教会",
    en: "Church",
    aliases: ["教会", "团契", "肢体", "长老", "牧养", "合一", "群体", "门徒群体"],
    description: "关于教会生活、群体关系、牧养与合一的文章。"
  },
  {
    id: "discipleship",
    zh: "门徒",
    en: "Discipleship",
    aliases: ["门徒", "跟随", "舍己", "背起十字架", "代价", "作基督门徒", "顺服"],
    description: "关于跟随耶稣、舍己、顺服和门徒训练的文章。"
  },
  {
    id: "prayer",
    zh: "祷告",
    en: "Prayer",
    aliases: ["祷告", "代祷", "祈求", "主祷文", "求问", "亲近神", "等候神"],
    description: "关于祷告、代求、亲近神和寻求神旨意的文章。"
  },
  {
    id: "suffering",
    zh: "苦难",
    en: "Suffering",
    aliases: ["苦难", "受苦", "试炼", "软弱", "眼泪", "困境", "患难", "烈火窑"],
    description: "关于苦难、试炼、软弱和神同在的文章。"
  },
  {
    id: "obedience",
    zh: "顺服",
    en: "Obedience",
    aliases: ["顺服", "遵行", "听从", "遵守", "服从", "神的旨意", "行道"],
    description: "关于听从神话语、遵行真理和顺服操练的文章。"
  },
  {
    id: "worship",
    zh: "敬拜",
    en: "Worship",
    aliases: ["敬拜", "荣耀神", "赞美", "以神为乐", "献为活祭", "感恩", "赞叹"],
    description: "关于敬拜、荣耀神、感恩和以神为乐的文章。"
  },
  {
    id: "gospel",
    zh: "福音",
    en: "Gospel",
    aliases: ["福音", "好消息", "救恩", "称义", "得救", "救主", "十字架上的福音"],
    description: "关于福音核心、救恩、称义和基督工作的文章。"
  },
  {
    id: "holy-spirit",
    zh: "圣灵",
    en: "Holy Spirit",
    aliases: ["圣灵", "保惠师", "灵里", "被圣灵", "圣灵引导", "圣灵浇灌", "圣灵感动"],
    description: "关于圣灵工作、引导、更新和能力的文章。"
  },
  {
    id: "cross",
    zh: "十字架",
    en: "Cross",
    aliases: ["十字架", "舍己", "受死", "宝血", "伟大的交换", "钉十字架"],
    description: "关于耶稣十字架、代赎、舍己和救赎的文章。"
  },
  {
    id: "resurrection",
    zh: "复活",
    en: "Resurrection",
    aliases: ["复活", "活过来", "新生命", "重生", "永生", "生命", "盼望"],
    description: "关于基督复活、重生、新生命和永生盼望的文章。"
  },
  {
    id: "kingdom-of-god",
    zh: "神的国",
    en: "Kingdom of God",
    aliases: ["神的国", "天国", "国度", "哪个国度", "王权", "君王", "主权"],
    description: "关于神掌权、天国价值和属神国度身份的文章。"
  },
  {
    id: "idolatry",
    zh: "偶像",
    en: "Idolatry",
    aliases: ["偶像", "贪心", "骄傲", "假神", "玛门", "拜偶像", "心中的福音"],
    description: "关于心中偶像、骄傲、贪心和错误敬拜对象的文章。"
  },
  {
    id: "sanctification",
    zh: "成圣",
    en: "Sanctification",
    aliases: ["成圣", "圣洁", "成长", "生命果子", "更新", "操练", "活出福音"],
    description: "关于生命成长、圣洁、更新和结出果子的文章。"
  },
  {
    id: "sin",
    zh: "罪",
    en: "Sin",
    aliases: ["罪", "罪恶", "犯罪", "论断", "试探", "诱惑", "人的罪恶"],
    description: "关于罪、试探、论断和人需要救恩的文章。"
  },
  {
    id: "forgiveness",
    zh: "饶恕",
    en: "Forgiveness",
    aliases: ["饶恕", "赦免", "不饶恕", "和好", "伸冤", "以善胜恶"],
    description: "关于赦免、饶恕、和好与把审判交给神的文章。"
  },
  {
    id: "justice",
    zh: "公义",
    en: "Justice",
    aliases: ["公义", "公平", "审判", "伸冤", "义", "定罪", "神公义吗"],
    description: "关于神的公义、审判、伸冤和称义的文章。"
  },
  {
    id: "identity",
    zh: "身份",
    en: "Identity",
    aliases: ["身份", "价值", "在耶稣里", "属主", "儿女", "收养", "仆人"],
    description: "关于在基督里的身份、价值和归属的文章。"
  },
  {
    id: "stewardship",
    zh: "管家",
    en: "Stewardship",
    aliases: ["管家", "才干", "托付", "财宝", "慷慨", "知足", "奉献"],
    description: "关于钱财、恩赐、托付、知足和慷慨的文章。"
  },
  {
    id: "wisdom",
    zh: "智慧",
    en: "Wisdom",
    aliases: ["智慧", "箴言", "分辨", "明辨", "听见神", "诊断", "根基"],
    description: "关于属灵智慧、分辨力和按真理生活的文章。"
  },
  {
    id: "evangelism",
    zh: "宣教",
    en: "Mission",
    aliases: ["宣教", "传讲", "见证", "未知之神", "福音的渗透力", "事工", "布道"],
    description: "关于见证、传福音、宣教和事工使命的文章。"
  },
  {
    id: "unity",
    zh: "合一",
    en: "Unity",
    aliases: ["合一", "和谐", "同心", "接纳", "彼此坚固", "共同信心", "冲突"],
    description: "关于在基督里合一、接纳和处理冲突的文章。"
  },
  {
    id: "fellowship",
    zh: "彼此相爱",
    en: "Fellowship",
    aliases: ["彼此相爱", "彼此", "团契", "相交", "彼此坚固", "彼此接纳"],
    description: "关于信徒彼此相爱、相交和互相扶持的文章。"
  },
  {
    id: "new-life",
    zh: "生命更新",
    en: "New Life",
    aliases: ["生命更新", "新生命", "成为新人", "重生", "改变", "恢复", "自由"],
    description: "关于重生、恢复、自由和生命改变的文章。"
  },
  {
    id: "truth",
    zh: "真理",
    en: "Truth",
    aliases: ["真理", "神的话", "圣经", "话语", "可靠准则", "道", "专心于神的话语"],
    description: "关于神的话语、真理根基和圣经权威的文章。"
  },
  {
    id: "eschatology",
    zh: "末世盼望",
    en: "Eschatological Hope",
    aliases: ["末世", "再来", "警醒", "审判", "等候主", "永恒", "荣耀"],
    description: "关于警醒等候、最终审判和永恒盼望的文章。"
  }
];

export const TOPIC_RULES: Record<string, string[]> = Object.fromEntries(
  KNOWLEDGE_TOPICS.map((topic) => [topic.zh, topic.aliases])
);

function normalizeTopicSource(value: string): string {
  return value.normalize("NFKC").toLocaleLowerCase("zh-CN");
}

export function inferTopics(input: TopicInput): string[] {
  const source = normalizeTopicSource(
    [
      input.title,
      input.description,
      input.scripture,
      ...(input.tags ?? []),
      cleanMarkdown(input.body ?? "")
    ]
      .filter(Boolean)
      .join(" ")
  );

  return KNOWLEDGE_TOPICS.filter((topic) =>
    topic.aliases.some((alias) => source.includes(normalizeTopicSource(alias)))
  ).map((topic) => topic.zh);
}
