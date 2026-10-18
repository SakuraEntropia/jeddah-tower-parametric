# 资料出处与版本边界

## 塔冠与体型

- **RWDI项目1011301，2012-01-18风荷载报告**，建筑立面图修订日期2011-11-23。使用图4d、6d、8d（完整190页PDF的第119、125、131页）的矢量轮廓和方向键图。报告Table1注明体型依据`2011.10.05 TOWER MASSING.3dm`；本项目没有该原始Rhino模型。[报告公开镜像](https://studylib.net/doc/28040482/wind-load-study---rwdi-final-report-18june12)。荷载分区虚线与填充不能充当阳台定位线。
- **Weismantle / Stochetti，CTBUH Journal2013，Case Study: Kingdom Tower, Jeddah**。图8典型截面用于主体平面；文中3.5m是楼板边缘悬挑原则，不是阳台进深实测值。3.0°、3.3°、3.6°为端部剪力墙倾角，不能据此任意使整条幕墙鼓出。
- [ASGG项目页](https://www.smithgill.com/work/jeddah_tower/)与[官方项目册](https://www.smithgill.com/media/pdfs/Jeddah_Tower_for_web.pdf)：体型、立面、裙房与观景台形态核对。
- [ASGG Ben Johnson项目讲座（2026）](https://wbowe.com/2026/04/26/jeddah-tower-the-worlds-tallest-building-ben-johnson/)：22:32上段剖面与平面，46:54阳台幕墙剖面。结构墙平面不直接等于完整幕墙外边界。

## 楼层

- ASGG2013-08-02面积/标高表：[AE-000A](https://www.scribd.com/document/877607755/AE-000A-130802)、[AE-000B](https://www.scribd.com/document/877607741/AE-000B-130802)。使用公开文本记录；L157=630m、L158=634m且仅463m²、L167=670m。未获得L158完整平面轮廓，因此本版省略该部分板。
- 2011 RWDI体型、2013楼层表和后续幕墙资料不被视作同一套施工文件。1008m是用户指定覆盖值。

## 幕墙

- [江河2025-11-22](https://en.jangho.com/JANGHONEWS/2025/1122/139.html)：幕墙系统分类及40mm接缝。
- [江河2025-12-03](https://en.jangho.com/JANGHONEWS/2025/1203/140.html)：首块幕墙单元1.5×5.3m，L18约+73.95m。该特定单元不用于推导全塔层高。横向约1.5m单元与ASGG早期幕墙资料一同核对。

## 观景台与裙房

- [Jeddah Economic Company技术演示公开版本](https://www.scribd.com/document/334535232/Kingdom-Tower)：观景台L157约630m、最大外悬约33m；钢框架、箱形桁架和横向构件。
- [Sinn / Weismantle结构系统说明](https://www.fullsdenginyeria.cat/kingdom-tower-structural-system-and-how-it-was-developed)：悬挑阳台、板边变化及观景台结构说明。
- ASGG官方项目图片用于形态核对，未获尺寸的直径、中心偏移、支撑及裙房控制点继续标记为拟合，未转成“已核定”尺寸。

## 原件指纹

`reports/reference_fingerprints.json`记录本地使用PDF的SHA-256，以区分资料版本。它们不是本仓库的重新分发文件。幕墙、阳台、裙房仍有缺项，详见[状态表](STATUS.md)。
