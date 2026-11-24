# EGA中文译校：2026-11-21 Dot整合完整续作工程

本包保存可直接继续工作的当前工程、13份底本、旧56批与新19批Dot来源，以及可逐字节恢复的旧工程。当前数学版本为“第十七版·第五卷增补第三辑”；本轮整理没有另译新段。

## 新对话从这里开始

1. 上传这个完整ZIP。
2. 请新对话先读 00_START_HERE/新对话接续提示.txt。
3. 核验全包后，进入 01_project/EGA_v17/，读取 PROGRESS.md、HANDOVER_STATE.json、SOURCE_MAP.md、PENDING_ISSUES.md 及实际源码末段。

当前可直接阅读的成品为 01_project/EGA_v17/main.pdf（1158页）和 report.pdf（287页）；独立源码为 single.tex 和 report_single.tex。

最近第五卷分支译至英译底本物理77页15.7末；下一处为英文78页附录17.16《光滑二次型》的16.1，对读法文物理161页。正式第IV章另从其底本物理221页提要开始。全部书籍未译完。

## 运行入口

```bash
python3 verify_package.py --strict
bash BUILD_ALL.sh
```

完整构建需要Python 3、XeLaTeX；逐页技术比对另需PyMuPDF。项目带有CTeX宏包、默认Fandol字体与许可等既有依赖，但不假称包含整个跨平台TeX发行版。详细方法见当前工程README.md。

## 历史保存方式

当前工程、底本和Dot原始档案是普通文件，可直接读取。额外历史中与这些文件字节相同的内容共用一份数据，独有内容置于 04_history/content/；04_history/RESTORE_INDEX.json 完整记录原路径、现存路径和SHA-256。没有把上一轮整个大ZIP逐层再套入新包，也没有改变原始Dot ZIP的字节。

恢复历史的例子：

```bash
python3 restore_versions.py --version v17 --destination /一个新的空目录
python3 restore_versions.py --version supplement_III --destination /另一个新的空目录
python3 restore_versions.py --version supplement_III_delta --destination /第三个新的空目录
```

这会还原原ZIP中普通文件的完整路径和字节，不能据此宣称生成的外层ZIP与原ZIP容器字节相同。当前续译不需要先恢复历史。完整说明见00_START_HERE/历史恢复工具说明.md。

工程包内00_START_HERE/工程核查摘要.md汇总本轮实际检查。文件完整、编译成功、像素一致及有限页面抽样均不代表所有数学证明已经独立审定。

## 后续改稿时的历史保护

历史版本所引用的现行TeX、源码和构建文件已另外按SHA保存不可变快照；后续修改工作稿不会改写这些历史字节。03_sources、05_Dot原始归档、vendor及明确的history目录仍作为共享原件，须保持不变；如需处理，请在另一个副本上操作。
