from bs4 import BeautifulSoup
import requests

'''类：工具箱'''
class neu():
    # 二级分类对象
    work = ""  #学业
    ipgw = ""  #校园网
    ecard = "" #校园卡
    
    # 构造函数：
    def __init__(self,stu_id,passwd):
        session = self.__login(stu_id,passwd) #登录
        
        if (session == False):
            raise Exception('登录失败！错误的用户名与密码。')
        self.__session = session
        
        #初始化二级类
        self.work = self.__work(session)  #查询
        self.ipgw = self.__ipgw(session)  #校园网
        self.ecard = self.__ecard(session)  #校园卡
    
    '''函数：登录neu'''
    '''输入：用户名，密码'''
    '''返回：session会话'''
    def __login(self,stu_id,passwd):

        #构造session请求
        a = requests.session()

        # 第一步：访问pass，获取登录参数
        try:
            r = a.get("https://pass.neu.edu.cn")
        except:
            r = a.get("http://pass.neu.edu.cn")

        ## 解析登录参数
        soup = BeautifulSoup(r.text,"html.parser") #解析登录参数
        ### lt参数
        lt = soup.find(attrs={"id":"lt"}).attrs['value']
        ### execution参数
        execution = soup.find(attrs={"name":"execution"}).attrs['value']
        ### _eventId参数
        _eventId = soup.find(attrs={"name":"_eventId"}).attrs['value']
        ### rsa参数
        rsa = str(stu_id) + str(passwd) + lt
        ### 构造登录数据字典
        data = {"rsa":rsa,
                "ul":str(len(str(stu_id))),
                "pl":str(len(str(passwd))),
                "lt":lt,
                "execution":execution,
                "_eventId":_eventId}

        # 第二步：提交登录请求
        try:
            r = a.post("https://pass.neu.edu.cn/tpass/login?service=",data=data)
        except:
            r = a.post("http://pass.neu.edu.cn/tpass/login?service=",data=data)
        
        # 判断是否登录成功
        if (r.url == 'https://pass.neu.edu.cn/tpass/login?service=' or r.url == 'http://pass.neu.edu.cn/tpass/login?service='):
            return False
        
        # 第三步：返回session
        return a 
    
    '''类：学业工具包'''
    class __work():
        __session = ""
        
        def __init__(self,__session):
            self.__session = __session
        
        '''函数：GPA查询器'''
        def gpa(self):
            r = self.__session.get('https://pass.neu.edu.cn/tpass/login?service=http://219.216.96.4/eams/teach/grade/course/person!search.action?semesterId=47')
            return float(r.text.split("总平均绩点：")[1].split('</div>')[0])   
        
        '''函数：考试查询器'''
        '''返回：考试科目列表'''
        def exam(self):
            #查询最近的考试类别
            r = self.__session.get('http://219.216.96.4/eams/stdExamTable.action')
            soup = BeautifulSoup(r.text,"html.parser")
            number = str(soup.option.attrs['value'])  #类别编号

            #获取考试列表
            r = self.__session.get('http://219.216.96.4/eams/stdExamTable!examTable.action?examBatch.id={}'.format(number))
            soup = BeautifulSoup(r.text,"html.parser")
            exam_list_raw = soup.table.tbody.find_all('tr')  #考试列表

            exam_list = []  #考试时间存储
            for exam in exam_list_raw:
                try:
                    exam_list.append({'科目':exam.find_all('td')[1].text,'时间':'{},{}'.format(exam.find_all('td')[3].text,exam.find_all('td')[4].text),'考场':exam.find_all('td')[5].text})
                except:
                    pass
            
            return exam_list
    
    '''类：校园卡类'''
    class __ecard():
        __session = ""
        
        '''函数：构造函数'''
        '''初始化session接口'''
        def __init__(self,session):
            self.__session = session
        
        '''函数：查询一卡通余额'''
        def money(self):
            #获取ticket
            r = self.__session.get('https://pass.neu.edu.cn/tpass/login?service=http://ecard.neu.edu.cn/selflogin/login.aspx')
            soup = BeautifulSoup(r.text,"html.parser")
            ticket_url = soup.find(attrs={'id':'form1'}).attrs['action']
            
            #合成访问登录接口
            r = self.__session.get("http://ecard.neu.edu.cn/selflogin/{}".format(ticket_url))
            soup = BeautifulSoup(r.text,"html.parser")
            #参数保存
            data = {}  #空字典
            argv_list = soup.form.find_all("input")
            for argv in argv_list:
                data[argv.attrs['name']] = argv.attrs['value']  #构造数据字典
            #登录
            r = self.__session.post("http://ecard.neu.edu.cn/selfsearch/SSOLogin.aspx",data=data)
            
            #获取基本信息
            r = self.__session.get("http://ecard.neu.edu.cn/selfsearch/User/baseinfo.aspx")
            money = float(r.text.split('<span id="ContentPlaceHolder1_txtOddFare" class="red">')[1].split('元')[0].strip())  #余额
            
            return money
             
    '''类：校园网类'''
    class __ipgw():
        __session = "" 
        
        def __init__(self,__session):
            self.__session = __session
        
        '''函数：连接校园网'''
        def connect(self):
            # 发送请求 登录网关
            r = self.__session.get('https://pass.neu.edu.cn/tpass/login?service=https%3A%2F%2Fipgw.neu.edu.cn%2Fsrun_cas.php%3Fac_id%3D15')
            
            return True
        
        '''函数：查询校园网钱包'''
        '''返回：剩余流量，余额'''
        def info(self):
            r = self.__session.get("https://pass.neu.edu.cn/tpass/login?service=http://ipgw.neu.edu.cn:8800/sso/default/neusoft")
            
            #已用流量
            used = float(r.text.split('<label>已用流量</label>')[1].split('G')[0].strip())
            #总流量
            if (r.text.find('27G') != -1):
                All = 27
            elif (r.text.find('60G') != -1):
                All = 60
            elif (r.text.find('5G') != -1):
                All = 5
            else:
                All = 0
            #剩余流量
            rest = round(All - used,2)
                
            #剩余金额
            money = float(r.text.split('<label>产品余额</label>')[1].split('<')[0].strip())
            
            return {'流量':rest,'余额':money}
