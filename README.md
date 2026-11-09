# one-step-report-skill

**One-Step Report v0.1** · 中文临床文献组会技能。输入研究论文及可用的补充材料，生成可编辑 PPT、逐页填充 Word 和演讲人汇报 Word。可附自己最新的参考幻灯片，也可直接使用[随包模板](assets/clinical-journal-club.potx)。

> **本技能完全由 AI 打造（100% AI-built）。** AI 根据用户提供的组会范例和反馈，制作了技能流程、文档、通用 PowerPoint 模板及检查脚本，并完成发布前验收。用户确定了目标、版式要求，并授权公开发布。实际汇报中的研究结论、数据与图表以所提供论文为出处。

## 安装与调用

从 [v0.1 Release](https://github.com/LightFury333/one-step-report-skill/releases/tag/v0.1) 下载 `one-step-report-v0.1.zip`，将解压后的整个 `one-step-report` 文件夹放入个人 Codex 技能目录（通常为 `~/.codex/skills/`）。检查 `one-step-report/SKILL.md` 与 `one-step-report/assets/` 同级存在。在能读取论文和制作 Office 文件的新会话中调用：

> 用 $one-step-report 解读附上的主文与补充材料，为临床组会制作 20 分钟的中文 PPT、逐页填充稿及演讲稿，另存到独立子文件夹。

已有三件套时也可以指定修改范围：

> 用 $one-step-report 把第 8 页的原图放大，补充读图说明，并同步两份 Word 的第 8 页段。

制作规则和验收方式见 [SKILL.md](SKILL.md)。运行时页数随论文与时长调整。通用模板可在 PowerPoint 中新建为普通 PPTX，使用者可继续编辑其中的文本和表格。

