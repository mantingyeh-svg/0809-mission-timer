#!/usr/bin/env python3
"""PreToolUse hook: block Write/Edit/MultiEdit calls that introduce
Simplified-Chinese-only characters, so all Chinese copy in this project
stays Traditional Chinese (per CLAUDE.md).

Reads the Claude Code hook JSON payload from stdin. On a match, prints a
{"decision":"block","reason":...} JSON object to stdout so Claude sees
why the write was rejected and can retry with Traditional Chinese.
"""
import json
import sys

# High-confidence Simplified-only characters (i.e. they differ from their
# Traditional form and are not themselves valid Traditional characters).
# Characters that are legitimately used in both scripts (e.g. 后, 里, 面,
# 千) are intentionally left out to avoid false positives.
SIMPLIFIED_CHARS = set(
    "国学会这说时门问间应还没现来长车东龙马鸟鱼风电云见亲儿头发业义为乐书买卖"
    "华关兴军农冲决净准减击划创删动励劳区医协单却历压厌双变叶号听启员响团园"
    "围图圆场坏块坚坝报担护拥换据摆摇数无旧显术机杀杂权条极构标树样检楼横欢"
    "欧毁气汉汇汤沟泪测济浅浇温湾湿满灭灯灵灾灿热爱猎猪献环现画疗盐监盖盘"
    "着码确离种积称穷笔简类粮紧纠纪约级纯纲纳纷纸纹线组细织终经结给络绝统"
    "继续维绵综绿缓编缘缩缺网罗罚义习艺节范药获营蓝虑虚虽补装视观规触计订"
    "认讨让训议记讲许论设访证评识诉诊词试诗话询详语误说请诸读课谁调谈谋谢"
    "谣谨谬贝负贡财责贤败账货质贫购贯贱贴贵贷贸费贺贼贾贿资赋赌赏赐赔赖赛"
    "赞赠赢赵趋跃践轧轨转轮软轰轻载较辉输辖辆边达迁过运还进远违连迟适选递"
    "逻遗邓邮邻郑释鉴门闪闭问闯闲间闷闸闹闻阅阔队阳阴阵阶际陆陈隐难雾静页"
    "顶项顺须顽顾顿预领频题颜额飞饭饮饰饱饿馆驱驶驻骂验骑骗鲁鲜鸡鸣鸭鸿鹅"
    "鹰麦齐齿龟"
)


def collect_texts(tool_name, tool_input):
    if tool_name == "Write":
        return [tool_input.get("content", "") or ""]
    if tool_name == "Edit":
        return [tool_input.get("new_string", "") or ""]
    if tool_name == "MultiEdit":
        return [e.get("new_string", "") or "" for e in (tool_input.get("edits") or [])]
    return []


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    texts = collect_texts(tool_name, tool_input)

    found = set()
    for text in texts:
        for ch in text:
            if ch in SIMPLIFIED_CHARS:
                found.add(ch)

    if found:
        chars = "、".join(sorted(found))
        reason = (
            "偵測到疑似簡體字："
            + chars
            + "。本專案規定所有中文文案一律使用繁體中文（見 CLAUDE.md），"
            + "請把上面這些字改成繁體後再寫入檔案。"
        )
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
