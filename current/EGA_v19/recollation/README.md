# 第十九版逐段回校证据

本目录保存 8.14 至 §11 的法英对读、反例、历史注释迁移及实际检查记录。reports/ 中的旧段落与旧注是历史证据，正文采用 current/EGA_v19/continuations 中的五份 v19 模块。

工程脚本 revise_root_sections.py、revise_section10.py、integrate_v19.py 是本轮一次性迁移脚本，使用了当时的工作路径；不要在新版本上重新执行。正式构建使用工程根 build.sh。

局部 section11_probe 是合并前的 8 页排版校样，并非最终整本验证。最终文件散列和整本验证见 checks/。恢复记录只覆盖本机实际取得的 777 个旧清单文件；不把未取回的 2322 个文件当成已本地核验。全部既有文件的检验在发布 runner 进行。

发布工具夹具没有收入本目录；其 DRAFT_VALIDATION 仅记录极小字节夹具和静态检查，不能代表实际全仓验证。
