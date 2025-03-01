
## PULL-Request
https://github.com/geeeeeeeeek/git-recipes/wiki/3.3-%E5%88%9B%E5%BB%BA-Pull-Request




## 华人开源社区萌新玩家 ISSUE / PR 指南
https://github.com/Dafrok/dafrok.github.io/issues/6
本文意在为华人开源社区玩家营造一个良好的交流环境。
如果您是开发者，在您遇到棘手的 ISSUE 或 PR 时，请将本文转发给相关贡献者。
如果您是贡献者，请耐心阅读本文，以便提高您与开发者的沟通效率。

### 基础
首先请花10分钟时间学习 markdown 语法和语义，使你的注释和评论不至于因为排版问题丧失可读性。
如果你发现自己关注的 ISSUE 或 PR 长时间没收到反馈或在预期外被关闭，请第一时间检查是否提供了足够详细的有效信息。
包括你在内的每个人的时间和精力是有限的，请牢记这一点。
### ISSUE 基本规范
如果项目中含有 CONTRIBUTING.md 文件，请严格参照该文件中的描述步骤发布 ISSUE。
如果项目不含有 CONTRIBUTING.md 文件，或文件中的描述有含糊不清的地方，请参考以下步骤发布 ISSUE。
### 参考
ISSUE 一般分为输出不符合预期、提供新的想法和建议两种常见类型。

1. 输出不符合预期
首先仔细阅读项目的文档，确保自己没有疏漏任何一个相关说明。
参考文档一步一步重现问题，直到找到输出不符合预期时的临界条件。
查看 ISSUE 列表里是否有人提出相同的 ISSUE。
如果有人提出过相同的 ISSUE，请直接参与讨论，或请参照该围绕 ISSUE 的讨论解决你的问题。
如果没有人提出相关 ISSUE，请开一个新 ISSUE，标题要言简意赅地表示出『哪段代码或什么操作』在『怎样的临界条件下』输出了『什么不符合预期的结果』。
此类 ISSUE 中应至少应该包含以下信息：
环境描述
项目版本
运行时版本（如 php 版本、浏览器版本）
系统版本
其它相关环境及环境变量
问题描述
问题的临界条件
详细复现步骤 - 如果步骤过于复杂，请尽可能使用在线运行环境（如 codepen）进行展示，或新建一个仓库提交用于复现问题的源码，使维护人员能方便地观察到问题的所在。
期望输出
实际输出
2. 提供新的想法和建议
首先仔细阅读项目的文档，确保自己没有疏漏任何一个相关说明。
查看 ISSUE 列表里是否有人提出相同的 ISSUE。
确保没有人和自己的想法和建议相同时，开一个新 ISSUE。
在 ISSUE 中说明你的想法和建议，并提出目前的弊端，以及你的想法能带来的优势。
如果开发者认同你的想法，你可以尝试去发 PR 来实现你的想法。
范例
N3-components/N3-components#27
ant-design/ant-design#3047
ecomfe/fecs-loader#9

### PR 基本规范
如果项目中含有 CONTRIBUTING.md 文件，请严格参照该文件中的描述步骤进行 PR。
如果项目不含有 CONTRIBUTING.md 文件，或文件中的描述有含糊不清的地方，请参考以下步骤进行 PR。
参考
PR 一般分为 bug 修复、新 feature 实现、修正拼写错误三种常见情况。

1. 修复 bug
当为一个开源项目修复 bug 时，需根据实际情况至少在 PR 的描述信息中提供以下信息：
    + 环境描述
    + 项目版本
    + 运行时版本（如 php 版本、浏览器版本）
    + 系统版本
    + 其它相关环境及环境变量
    + bug 现象描述
    + bug 出现原因
    + 详细复现步骤 - 如果步骤过于复杂，请尽可能使用在线运行环境（如 codepen）进行展示，或新建一个仓库提交用于复现问题的源码，使维护人员能方便地观察到问题的所在。
    + 期望输出
    + 实际输出
    + 修复方式描述

2. 新 feature 实现
如果对开源项目有改进的想法，应在提交 PR 之前，首先查看 ISSUE 列表里是否有相同的需求。
如果没有，则要先提 ISSUE 询问维护者是否有关于新 feature 的打算和构想。
如果 ISSUE 被标记为 enhancement / feature ，或者维护者明确表示支持你的想法时，你就可以向该项目发 PR 了。
发 PR 时不要忘记在描述中用 "#" 关联上面的 ISSUE ID。
如果项目中涉及测试环节，请记住为新特性写相关的单元测试。通过所有的单元测试后才能提交。
3. 文档 / 描述 / 注释 等措辞、拼写或排版错误
此类情况没有很严格的规范，排版和拼写问题直接指出错误的地方即可。
措辞方面如果涉及歧义或概念问题，请引用一些权威的参考资料佐证自己的观点，确保用词严谨。

范例
Microsoft/TypeScript#10980
N3-components/N3-components#26
