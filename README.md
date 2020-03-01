# everwork的自说明文档

## 把evernote作为信息存储收集和展示发布平台的工作平台

### 志在千里

### 天天向上

- *微操作构建天堂*
- *勤练脑改善生活*

---

#### 流程图

```flow
    //定义类型和描述
    st=>start: 开始
    e=>end: 结束
    op=>operation: 测试
    cond=>condition: 无误？

    st->op->cond
    cond(yes)->e
    cond(no)->op
```

```python
## 操作块(格式为:变量=>操作块: 备注名)
st=> start: 开始
e=>end: 结束
#普通操作块 opration
op1=>opration: 第一个操作块
op2=>opration: 第二个操作块
#判断块 condition
cond1=>condition: 第一个判断
cond2=>condition: 第二个判断
  
#输入输出块 inputoutput[平行四边形]
io1=>inputoutput: 输入输出块1
io2=>inputoutput: 输入输出块2
#子任务块
sub1=>subroutine: 子任务1
sub2=>subroutine: 子任务2
  
## 判断和位置控制
#判断流程控制
cond1(yes)->op1  #yes 的时候回到 op1
cond1(no)->e   #no 的时候 去结束
  
#位置指定
cond1(no)->op2(right)->op1 #控制 op2 位置置于右边，再由op2 返回 op1 (好像不能向左)
#还可以这样 cond1(no,right)
cond1(yes)->e

## 流程控制
#分着写
st->op1
op1->e
  
#合着写
st->op1->e
  
#判断也是一样：
st->cond
cond(yes)->io
cond(no)->op1
```

```flow
    st=>start: 鉴权
    e=>end: 结束退出
    cond1=>condition: user==bgbiao
    product=ddaotian
    productcheck=>condition: ddaotian类型产品库存
    (ecs,bss,vpc,eip,hids)

    op1=>operation: 发起预订请求
    拆单并库存检测

    op2=>operation: info:生产指定类型产品
    (DAOTIAN:ecs,natip,eip,hids)
    op3=>operation: 鉴权失败
    op4=>operation: 库存检测失败

    io1=>inputoutput: 返回产品相关信息
    ECS,NATIP,EIP,HIDS

    io2=>inputoutput: info:无此类型产品

    st->cond1
    cond1(yes)->op1->productcheck(yes)->op2->io1->e
    cond1(no)->op3->e
    cond1(yes)->op1->productcheck(no)->op4->io2->e
```

### 时序图

```sequence {theme="hand"}
    bgbiao-> bianbian: good morning
    note left of bgbiao: man
    bianbian -> bgbiao: eat something
    note right of bianbian: woman

    note over bgbiao: test

```

#### 流程图 under mermaid

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

#### 时序图 under mermaid

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->John: Hello John, how are you?
    loop Healthcheck
        John->John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail...
    John-->Alice: Great!
    John->Bob: How about you?
    Bob->Alice: Hi, how are you?
    Bob-->John: Jolly good!
```

#### mermaid甘特图

```mermaid
gantt
        dateFormat  YYYY-MM-DD
        title Adding GANTT diagram functionality to mermaid
        section A section
        Completed task            :done,    des1, 2014-01-06,2014-01-08
        Active task               :active,  des2, 2014-01-09, 3d
        Future task               :         des3, after des2, 5d
        Future task2               :         des4, after des3, 5d
        section Critical tasks
        Completed task in the critical line :crit, done, 2014-01-06,24h
        Implement parser and jison          :crit, done, after des1, 2d
        Create tests for parser             :crit, active, 3d
        Future task in critical line        :crit, 5d
        Create tests for renderer           :2d
        Add to mermaid                      :1d
```

#### mermaid甘特图1

```mermaid
gantt
title 甘特图
dateFormat YYYY-MM-DD
section 行1
任务1 :a1, 2014-01-01, 30d
任务2 :after a1 , 20d
section 行2
任务3 :2014-01-12 , 12d
任务4 : 24d
```

#### mermaid类图

可以看到大部分类关系（如聚合、继承）的显示都有问题，所以并不适合用于描述类与类之间的关系。

``` mermaid
classDiagram
Class01 <|-- AveryLongClass : Cool
Class03 *-- Class04
Class05 o-- Class06
Class07 .. Class08
Class09 --> C2 : Where am i?
Class09 --* C3
Class09 --|> Class07
Class07 : equals()
Class07 : Object[] elementData
Class01 : size()
Class01 : int chimp
Class01 : int gorilla
Class08 <--> C2: Cool label
```
