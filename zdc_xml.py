# coding:utf-8
import xml.etree.ElementTree as ET


ZDC_PR = []
pro_prlist = []
data_name_list = []
cj_hsc = "ZF0"  # 厂家代码 'S1E'"ZF0"
base_path = "C:\\Users\\CF-54\\Desktop\\ZDC\\"
b_name = "v0631S052GD___BCM_EL6_2H5_1X0"  # ZDC文件名 v07404012GD___Lenkung v0631S052GD___BCM v0631S052GD___BCM_EL6_2H5_1X0
prnum = "LFV2B2A15L5417572"  # 这里输入包含PR号文件名
try:
    tree = ET.parse(base_path+b_name+".xml")
    root = tree.getroot()
except FileNotFoundError:
    print("\033[0;31m异常，ZDC文件未找到，名字是不是复制错了？\033[0m")
    exit()


def union_dict(data):
    """相同键的值累加的函数"""
    _keys = set(sum([list(d.keys()) for d in data],[]))
    _total = {}
    for _key in _keys:
        _total[_key] = sum([d.get(_key,0) for d in data])
    return _total


def pro_pr():
    """车辆数据里面的PR号"""
    file = "C:\\Users\\CF-54\\Desktop\\ZDC\\"+prnum+".prnr"
    # file = r"C:\Users\CF-54\Desktop\ZDC\kombi.prnr"
    try:
        with open(file, "r") as f:
            lines = f.readlines()
            for line in lines:
                pro_prlist.append(line.strip())
    except FileNotFoundError:
        print("\033[0;31m异常，PR号文件未找到\033[0m")
    else:
        zdc_test()


def zdc_test():
    """ZDC的基本信息"""
    global pr_list
    dataid = root[0].find("DATEIID").text
    ver = root[0].find("VERSION-INHALT").text
    print("ZDC零件号：{}，版本：{}".format(dataid, ver))
    #  获取控制器的诊断信息
    dig_id = root[2][0][0].find("ADR").text
    dig_kwp = root[2][0][0].find("KWP").text
    dig_bus = root[2][0][0].find("BUS").text
    print("该控制器诊断类型：{0},诊断地址：{1},诊断协议：{2}".format(dig_bus, dig_id, dig_kwp))
    #  获取ZDC中PR号集合
    for REFFAM in root[2][0][1][0].iter("REFFAM"):
        for PR in REFFAM.findall("PRNR"):
            ZDC_PR.append(PR.text)
    #  获得共同的PR号集合
    pr_list = [x for x in pro_prlist if x in ZDC_PR]
    # print("共同PR号是： {}".format(pr_list))
    #  判断是否有厂家代码及获取ZDC中厂家代码
    #  如果xml里面没有厂家代码标签，hscs = root[2][0][1][1].findall("HSC")为空，但是不会触发异常这个很奇怪
    hscs = root[2][0][1][1].findall("HSC")
    if hscs:
        hsc_list = []
        for hsc in hscs:
            hsc_list.append(hsc.text)
        print("控制器厂家代码：{}".format(hsc_list))
        print("\033[1;31m厂家的代码选择为ZF0\033[0m")
        print("***"*18)
        for tabelle in root[2][0][1].iter("TABELLE"):
            bm_hsc = tabelle.find("HSC").text  # 编码中的厂家代码
            if bm_hsc == cj_hsc:  # 有厂家代码，TAB里面代码符合这一次循环才可以 'S1E'"ZF0"
                # print("厂家的代码选择为{}".format(bm_hsc))
                zdc_get(tabelle)
        #  下面是参数 直接索引-1不知道会不会有问题 QAQ
        for datenbereich in root[2][0][-1].iter("DATENBEREICH"):
            data_name = datenbereich.find("DATEN-NAME")
            if data_name.text in data_name_list:
                print("\033[0;34mPROGRAMMIERUNG  {}  START-ADR：{}\033[0m".format(data_name.text, datenbereich.find("START-ADR").text))
                print("{}".format(datenbereich.find("DATEN").text))
    else:
        print("\033[0;32mZDC: {}无厂家代码\033[0m".format(root[0].find("DATEINAME").text))
        for tabelle in root[2][0][1].iter("TABELLE"):
            zdc_get(tabelle)
        #  下面是参数
        for datenbereich in root[2][0][-1].iter("DATENBEREICH"):
            data_name = datenbereich.find("DATEN-NAME")
            if data_name.text in data_name_list:
                print("\033[0;34mPROGRAMMIERUNG  {}  START-ADR：{}\033[0m".format(data_name.text, datenbereich.find("START-ADR").text))
                print("{}".format(datenbereich.find("DATEN").text))


def zdc_get(tabelle):
    """处理一个ID的zdc内容"""
    global tegue
    zdc_val = []
    try:
        bm_id = tabelle.find("RDIDENTIFIER").text
        print("\033[0;34mKALIBRIERUNG:  {}\033[0m".format(bm_id))
        for fam in tabelle[-1].iter("FAM"):  # tabelle[-1]是TAB，每一个fam都是一个家族
            flag, flag1, flag2, x = 0, 0, 0, 0  # 作用域一定要搞清楚，要不然上一个循环的值会遗留到下一个循环
            famnum = fam.find("FAMNR").text
            #  编码的PR号
            for tegue in fam.iter("TEGUE"):  # tegue，就是单行的["1TV/1TY+2H0/2H5+7X4"]
                flag2 += 1
                # 处理PR号,有的是+开头，所有用strip方法删除。["1TV/1TY+2H0/2H5+7X4"]分成1TV/1TY 2H0/2H5 7X4 三组
                pr_oks = tegue.find("PRNR").text.strip('+').split("+")
                x = len(pr_oks)
                for s in pr_oks:  # s 是["1TV/1TY+2H0/2H5+7X4"]中的"1TV/1TY"
                    prs = s.replace("/", "")
                    for i in range(0, len(prs), 3):  # i是1TV
                        pr_cj = prs[i:i + 3]  # 裁剪出PR号pr_cj
                        if pr_cj in pr_list:  # 判断每一个单独的PR是否在pr_list里面
                            x -= 1
                            break
                        else:
                            continue
                if x == 0:  # 此处判断家族号下的细分配置["1TV/1TY+2H0/2H5+7X4"]的总体结果是都符合的
                    flag = 1
                    break
                else:  # 有可能第一小行没有匹配的PR号，第二行才对
                        flag1 += 1
                        continue
            if flag == 1:  # 此处判断家族号对应那一行的总体结果是合格的，["1TV/1TY+2H0/2H5+7X4"]
                for knoten in tegue.iter("KNOTEN"):
                    stelle = int(knoten.find("STELLE").text, base=16)  # stelle是第一位
                    lsb = int(knoten.find("LSB").text)       # lsb 是指数
                    wert = int(knoten.find("WERT").text, base=16)
                    val = {stelle: wert * (2 ** lsb)}
                    zdc_val.append(val)
            if flag1 == flag2:
                for knoten in tegue.iter("KNOTEN"):
                    error_stelle = int(knoten.find("STELLE").text, base=16)  # stelle是第一位
                    error_lsb = knoten.find("LSB").text      # lsb 是指数
                    val = {error_stelle: 100000}
                    zdc_val.append(val)
                print("\033[1;31m地址：{0} 家族号：{1} Bit位：{2} 没有匹配的PR号无法计算!\033[0m".format(bm_id, famnum, error_lsb))
            flag2 = 0
        dic_val = union_dict(zdc_val)  # 得到一个字典
        for i in sorted(dic_val.keys()):
            if dic_val.get(i) > 99999:
                print("\033[0;31m??\033[0m", end=' ')
            else:
                print('{0:02X}'.format(dic_val.get(i)), end=' ')
        print()
    except AttributeError:
        for cs_fam in tabelle[-1].iter("FAM"):
            for cs_fam in tabelle[-1].iter("FAM"):  # tabelle[-1]是TAB，每一个fam都是一个家族
                cs_flag, cs_flag1, cs_flag2, cs_x = 0, 0, 0, 0  # 作用域一定要搞清楚，要不然上一个循环的值会遗留到下一个循环
                cs_famnum = cs_fam.find("FAMNR").text
                #  参数的PR号
                for tegue in cs_fam.iter("TEGUE"):  # tegue，就是单行的["1TV/1TY+2H0/2H5+7X4"]
                    cs_flag2 += 1
                    # 处理PR号,["1TV/1TY+2H0/2H5+7X4"]分成1TV/1TY 2H0/2H5 7X4 三组
                    cs_pr_oks = tegue.find("PRNR").text.split("+")
                    cs_x = len(cs_pr_oks)
                    for s in cs_pr_oks:  # s 是["1TV/1TY+2H0/2H5+7X4"]中的"1TV/1TY"
                        cs_prs = s.replace("/", "")
                        for i in range(0, len(cs_prs), 3):  # i是1TV
                            cs_pr_cj = cs_prs[i:i + 3]  # 裁剪出PR号pr_cj
                            if cs_pr_cj in pr_list:  # 判断每一个单独的PR是否在pr_list里面
                                cs_x -= 1
                                break
                            else:
                                continue
                    if cs_x == 0:  # 此处判断家族号下的细分配置["1TV/1TY+2H0/2H5+7X4"]的总体结果是都符合的
                        cs_flag = 1
                        break
                    else:  # 有可能第一小行没有匹配的PR号，下一行才对
                        cs_flag1 += 1
                        continue
                if cs_flag == 1:  # 此处判断家族号对应那一行的总体结果是合格的，["1TV/1TY+2H0/2H5+7X4"]
                    for knoten in tegue.iter("KNOTEN"):
                        cs_names = knoten.findall("DATEN-NAME")
                        for i in cs_names:
                            data_name_list.append(i.text)
                if cs_flag1 == cs_flag2:
                    print("\033[1;31m家族号：{}参数的PR号无法计算！\033[0m".format(cs_famnum))
                cs_flag2 = 0


if __name__ == "__main__":
    pro_pr()


