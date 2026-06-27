import { cleanMarkdown } from "./text";

export interface TopicInput {
  title?: string;
  description?: string;
  scripture?: string;
  tags?: string[];
  body?: string;
}

const TOPIC_RULES: Record<string, string[]> = {
  "恩典": ["恩典", "白白", "礼物", "赐给"],
  "信心": ["信心", "相信", "信靠"],
  "十字架": ["十字架", "舍己", "钉十字架"],
  "自由": ["自由", "释放", "捆绑"],
  "祷告": ["祷告", "代祷", "祈求"],
  "盼望": ["盼望", "指望", "等候"],
  "爱": ["爱", "相爱", "怜悯"],
  "悔改": ["悔改", "回转", "认罪"],
  "门徒": ["门徒", "跟随", "作主门徒"],
  "圣灵": ["圣灵", "保惠师", "灵里"],
  "教会": ["教会", "肢体", "团契"],
  "福音": ["福音", "好消息", "救恩"]
};

export function inferTopics(input: TopicInput): string[] {
  const source = [
    input.title,
    input.description,
    input.scripture,
    ...(input.tags ?? []),
    cleanMarkdown(input.body ?? "")
  ]
    .filter(Boolean)
    .join(" ");

  return Object.entries(TOPIC_RULES)
    .filter(([, keywords]) => keywords.some((keyword) => source.includes(keyword)))
    .map(([topic]) => topic);
}

export { TOPIC_RULES };
