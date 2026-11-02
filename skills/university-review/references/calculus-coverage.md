# 大学高数考点索引

这个索引用于把用户只发送的题目路由到更具体的知识点、视频关键词和同类练习。它覆盖常见大学高等数学上下册的主干内容；不同学校的章节顺序和符号可能不同。

## 一元函数与微积分

| 知识点 | 推荐编号 | 常见方法或检索词 |
| --- | --- | --- |
| 函数、定义域、数列与函数极限 | `CALC.FUNCTION.BASIC`、`CALC.SEQUENCE.LIMIT`、`CALC.LIMIT.BASIC` | 定义域、单调有界、等价无穷小、夹逼、三角极限 |
| 洛必达法则与极限 | `CALC.LIMIT.LHOPITAL` | 洛必达、未定式 |
| 连续性与间断点 | `CALC.CONTINUITY` | 连续、间断点、介值定理 |
| 导数与微分 | `CALC.DERIVATIVE.BASIC`、`CALC.DERIVATIVE.HIGHER`、`CALC.DERIVATIVE.DIFFERENTIAL` | 链式法则、隐函数、参数方程、高阶导数、线性近似 |
| 微分中值定理 | `CALC.DERIVATIVE.MEANVALUE` | Rolle、拉格朗日、柯西中值定理 |
| 导数应用 | `CALC.DERIVATIVE.APPLICATION` | 单调性、极值、凹凸、渐近线、最值、曲率 |
| 不定积分 | `CALC.INT.SUBSTITUTION`、`CALC.INT.SECOND_SUBSTITUTION`、`CALC.INT.PARTS`、`CALC.INT.RATIONAL`、`CALC.INT.TRIG` | 凑微分、换元、分部、部分分式、有理函数与三角积分 |
| 定积分与积分性质 | `CALC.INT.DEFINITE` | 牛顿—莱布尼茨、换序、积分不等式 |
| 反常积分 | `CALC.INT.IMPROPER` | 无穷区间、无界函数、收敛性 |
| 定积分应用 | `CALC.INT.APPLICATION` | 面积、体积、弧长、旋转体、物理量应用 |
| 泰勒公式 | `CALC.TAYLOR` | 泰勒展开、余项、近似计算 |

## 级数

| 知识点 | 推荐编号 | 常见方法或检索词 |
| --- | --- | --- |
| 数项级数基本性质 | `CALC.SERIES.NUMERIC` | 正项级数、比较、极限比较 |
| 交错级数与绝对收敛 | `CALC.SERIES.ALTERNATING` | Leibniz、绝对收敛、条件收敛 |
| 比值、根值与积分判别 | `CALC.SERIES.TESTS` | 比值判别、根值判别、积分判别 |
| 幂级数 | `CALC.SERIES.POWER` | 收敛半径、收敛区间、逐项求导 |
| Taylor/Maclaurin 级数 | `CALC.SERIES.TAYLOR` | 展开、端点、误差 |
| Fourier 级数（教材包含时） | `CALC.SERIES.FOURIER` | 正弦级数、余弦级数、周期延拓 |

## 多元函数、重积分与向量分析

| 知识点 | 推荐编号 | 常见方法或检索词 |
| --- | --- | --- |
| 空间解析几何与向量 | `CALC.GEOMETRY.VECTOR`、`CALC.GEOMETRY.SPACE` | 直线、平面、距离、夹角、二次曲面 |
| 多元函数极限与连续 | `CALC.MULTI.LIMIT` | 二元极限、路径、连续性 |
| 偏导、全微分与链式法则 | `CALC.MULTI.PARTIAL`、`CALC.MULTI.DIFFERENTIAL`、`CALC.MULTI.CHAIN` | 偏导、全微分、复合函数 |
| 方向导数与梯度 | `CALC.MULTI.GRADIENT` | 方向导数、梯度、切平面 |
| 多元函数极值 | `CALC.MULTI.EXTREMA` | Hessian、条件极值、拉格朗日乘子 |
| 二重积分 | `CALC.MULTI.DOUBLE` | 直角坐标、极坐标、换序、对称性 |
| 三重积分 | `CALC.MULTI.TRIPLE` | 直角坐标、柱坐标、球坐标、Jacobian |
| 第一、二类曲线积分 | `CALC.VECTOR.LINE1`、`CALC.VECTOR.LINE2` | 参数化、路径无关、势函数 |
| 第一、二类曲面积分 | `CALC.VECTOR.SURFACE1`、`CALC.VECTOR.SURFACE2` | 参数曲面、法向量、通量 |
| Green、Gauss、Stokes 公式 | `CALC.VECTOR.GREEN`、`CALC.VECTOR.GAUSS`、`CALC.VECTOR.STOKES` | 环流、散度、旋度 |

## 常微分方程

| 知识点 | 推荐编号 | 常见方法或检索词 |
| --- | --- | --- |
| 可分离变量方程 | `CALC.ODE.SEPARABLE` | 分离变量、初值问题 |
| 一阶线性方程 | `CALC.ODE.LINEAR1` | 积分因子 |
| 齐次方程与 Bernoulli 方程 | `CALC.ODE.HOMOGENEOUS1`、`CALC.ODE.BERNOULLI` | 一阶齐次、Bernoulli |
| 二阶常系数线性方程 | `CALC.ODE.LINEAR2` | 特征根、待定系数、共振 |
| 可降阶高阶方程 | `CALC.ODE.REDUCIBLE` | 不显含 y、一次积分 |
| Euler 方程及初值问题 | `CALC.ODE.EULER`、`CALC.ODE.INITIAL_VALUE` | Cauchy-Euler、初值条件 |

## 使用边界

- 这些编号是推荐路由标签；现有 JSON 题库只包含少量原创演示题，不代表每个标签都有现成题目。
- 题库没有对应标签时，应说明“本地题库暂无”，再提供经过独立复算的 AI 生成变式，并标明来源。
- 面对证明题、含多个方法的综合题或教材特有专题，要先拆出主考点；若无法可靠推导，说明不确定点，不要只因分类表中有相似章节就保证能够完整解答。
- 线性代数、概率论、复变函数、偏微分方程和数学分析专题不自动归入本 Skill 的高数范围。
- 涉及定理时必须检查定义域和适用条件；涉及重积分时检查区域、方向和 Jacobian；涉及级数时检查端点；涉及 Fourier 级数时说明收敛点取值约定。
