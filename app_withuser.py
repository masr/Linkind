# coding=utf-8
from flask import Flask
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, validates
from flask.ext import admin, wtf
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView
from sqlalchemy.dialects import mysql


dbengine = create_engine('mysql://root:msheric@localhost/linkind?charset=utf8', echo=True)
Session = sessionmaker(bind=dbengine)
dbsession = Session()
#####################################################################################
#
#                        Model Definition
#
#####################################################################################
Base = declarative_base()

page_item_mapping = Table('page_item_mapping', Base.metadata,
    Column('page_id', Integer, ForeignKey('page.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('item.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), nullable=False, unique=True)
    password = Column(String(30), nullable=False)
    email = Column(String(30))
    cre_date = Column(DateTime)

    pages = relationship('Page')
    items = relationship('Item')

    @validates('email')
    def validate_email(self, key, email):
        if email:
            assert '@' in email
            return email

    def __unicode__(self):
        return self.name


class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(50), nullable=False)
    desc = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    cre_date = Column(DateTime)

    user = relationship('User')
    items = relationship('Item', secondary=page_item_mapping)
    __table_args__ = (
        UniqueConstraint('title', 'user_id'),
        )


    def __unicode__(self):
        return self.title


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    desc = Column(Text)
    color = Column(Enum('red', 'blue', 'yellow', 'white', 'green', 'gray', 'orange'), default='blue')
    size = Column(Enum('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'), default='5')
    cre_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    user = relationship('User')
    pages = relationship('Page', secondary=page_item_mapping)
    links = relationship('Link', primaryjoin='or_(Item.id==Link.id1,Item.id==Link.id2)')
    __table_args__ = (
        UniqueConstraint('name', 'user_id'),
        )

    def __unicode__(self):
        return self.name


class Link(Base):
    __tablename__ = 'link'
    desc = Column(Text)
    cre_date = Column(DateTime)
    id1 = Column(Integer, ForeignKey('item.id'), primary_key=True)
    id2 = Column(Integer, ForeignKey('item.id'), primary_key=True)

    item1 = relationship('Item', primaryjoin='Item.id==Link.id1')
    item2 = relationship('Item', primaryjoin='Item.id==Link.id2')


    def __unicode__(self):
        return "<%s , %s>" % self.item1 % self.item2

#####################################################################################
#
#                          Route
#
#####################################################################################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'msheric'

@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.route('/syncdb')
def syncdb():
    Base.metadata.drop_all(dbengine)
    Base.metadata.create_all(dbengine)

    maosuhan = User(name='maosuhan', password='msheric', email='smao@ebay.com')
    zhaojie = User(name='zhaojie', password='msheric')

    page = Page(title='历史',
        desc='中国历史从盘古、上帝、女娲等神话时代算起约有5000年；自夏朝算起约有4200年；从三皇五帝算起约有4600年；从中国第一次建立大一统中央集权制的秦朝开始算起约有2200年。')
    page.user = maosuhan
    page2 = Page(title='文学')
    page2.user = maosuhan
    page3 = Page(title='时尚')
    page3.user = zhaojie

    item = Item(name='李世民',
        desc='唐太宗李世民，陇西成纪人，祖籍陇西成纪或 赵郡隆庆，是唐朝第二位皇帝，627年9月4日－649年7月10日在位，年号贞观。他名字的意思是“济世安民”。他是杰出的军事家，在唐朝的建立与统一过程中立下赫赫战功发挥了决定性作用，爱好文学与书法，有墨宝传世。',
        color='yellow',
        size=8)
    item.user = maosuhan
    item.pages.append(page)

    item2 = Item(name='李渊',
        desc='唐高祖李渊（566年1月13日—635年），字叔德，祖籍陇西成纪（今甘肃秦安），唐朝开国皇帝，杰出的政治家和战略家。李渊出身于北朝的关陇贵族，七岁袭封唐国公。隋末天下大乱时，李渊乘势从太原起兵，攻占长安。公元618年5月，李渊称帝，国号唐，定都长安，不久之后便统一了全国。玄武门之变后，李渊退位成为太上皇。贞观九年，李渊病逝。谥号太武皇帝，庙号高祖，葬在献陵。唐高宗上元元年（674年）八月，改上尊号为神尧皇帝。唐玄宗天宝十三载二月，上尊号神尧大圣大光孝皇帝。',
        color='yellow',
        size=6)
    item2.user = maosuhan
    item2.pages.append(page)

    item3 = Item(name='魏征',
        desc='魏徵（580年－643年2月11日），字玄成。汉族，唐巨鹿人（今河北邢台市巨鹿县人，又说河北晋州市或河北馆陶市）人，唐朝政治家。曾任谏议大夫、左光禄大夫，封郑国公，谥文贞，以直谏敢言著称，是中国史上最负盛名的谏臣。著有《隋书》序论，《梁书》、《陈书》、《齐书》的总论等。其言论多见《贞观政要》。其中最著名，并流传下来的谏文表---《谏太宗十思疏》。他的重要言论大都收录在唐时王方庆所编《魏郑公谏录》和吴兢所编《贞观政要》两书里。为凌烟阁二十四功之一。',
        color='green',
        size=5)
    item3.user = maosuhan
    item3.pages.append(page)

    item4 = Item(name='隋炀帝',
        desc='隋炀帝杨广（569年－618年4月11日），华阴人（今陕西华阴），生于隋京师长安，是隋朝第二代皇帝，唐朝谥炀皇帝，夏王窦建德谥闵皇帝，其孙杨侗谥为世祖明皇帝。一名英，小字阿麽。隋文帝杨坚、独孤皇后的次子，开皇元年（581年）立为晋王，开皇二十年（600年）十一月立为太子，仁寿四年（604年）七月继位。他在位期间修建大运河（开通永济渠、通济渠，加修邗沟、江南运河），营建东都迁都洛阳城，开创科举制度，亲征吐谷浑，三征高句丽，因为滥用民力，造成天下大乱直接导致了隋朝的灭亡，618年在江都被部下缢杀。《全隋诗》录存其诗40多首。',
        color='yellow',
        size=7)
    item4.user = maosuhan
    item4.pages.append(page)

    link = Link(desc='父子')
    link.item1 = item
    link.item2 = item2

    link2 = Link(desc='君臣')
    link2.item1 = item
    link2.item2 = item3

    dbsession.add_all([maosuhan, zhaojie, page, page2, page3, item, item2, item3, item4, link, link2])
    dbsession.commit()

    return 'ok'


#####################################################################################
#
#                     Admin
#
#####################################################################################

class CKTextAreaWidget(wtf.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(wtf.TextAreaField):
    widget = CKTextAreaWidget()


class UserAdminView(ModelView):
    column_exclude_list = ['password']


class PageAdminView(ModelView):
    form_overrides = dict(desc=CKTextAreaField)
    column_searchable_list = ['title', 'desc']
    column_labels = dict(desc='Description')
    column_filters = ['user']


class ItemAdminView(ModelView):
    form_overrides = dict(desc=CKTextAreaField)
    column_searchable_list = ['name', 'desc']
    column_labels = dict(desc='Description')
    column_filters = ['user']


class LinkAdminView(ModelView):
    form_overrides = dict(desc=CKTextAreaField)
    column_searchable_list = ['desc']
    column_labels = dict(desc='Description', item1='Item', item2='Item')
    column_filters = ['user']


admin = Admin(app, name='Linkind Admin')
admin.add_view(UserAdminView(User, dbsession))
admin.add_view(ModelView(Page, dbsession))
admin.add_view(ItemAdminView(Item, dbsession))
admin.add_view(LinkAdminView(Link, dbsession))

#####################################################################################
#
#                         Start App
#
#####################################################################################
app.debug = True
app.run('0.0.0.0', 8000)