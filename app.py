# coding=utf-8
from flask import Flask
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext import admin, wtf
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView


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


class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(50), nullable=False, unique=True)
    desc = Column(Text)
    cre_date = Column(TIMESTAMP, server_default=text('NOW()'), nullable=False)

    items = relationship('Item', secondary=page_item_mapping)


    def __unicode__(self):
        return self.title


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False, unique=True)
    desc = Column(Text)
    color = Column(Enum('red', 'blue', 'yellow', 'white', 'green', 'gray', 'orange'), default='blue', nullable=False)
    size = Column(Enum('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'), default='5', nullable=False)
    cre_date = Column(TIMESTAMP, server_default=text('NOW()'), nullable=False)

    pages = relationship('Page', secondary=page_item_mapping)
    links = relationship('Link', primaryjoin='or_(Item.id==Link.id1,Item.id==Link.id2)')


    @hybrid_property
    def neighbors(self):
        items = [link.item1 for link in self.links if link.item1.name != self.name]
        items.extend([link.item2 for link in self.links  if link.item2.name != self.name])
        return items

    def __unicode__(self):
        return self.name


class Link(Base):
    __tablename__ = 'link'
    desc = Column(Text)
    size = Column(Enum('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'), default='5', nullable=False)
    cre_date = Column(TIMESTAMP, server_default=text('NOW()'), nullable=False)
    id1 = Column(Integer, ForeignKey('item.id'), primary_key=True)
    id2 = Column(Integer, ForeignKey('item.id'), primary_key=True)

    item1 = relationship('Item', primaryjoin='Item.id==Link.id1')
    item2 = relationship('Item', primaryjoin='Item.id==Link.id2')


    def __unicode__(self):
        return "<%s , %s>" % (unicode(self.item1), unicode(self.item2))

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

    page = Page(title=u'历史',
        desc=u'中国历史从盘古、上帝、女娲等神话时代算起约有5000年；自夏朝算起约有4200年；从三皇五帝算起约有4600年；从中国第一次建立大一统中央集权制的秦朝开始算起约有2200年。')
    page2 = Page(title=u'文学')
    page3 = Page(title=u'时尚')

    item = Item(name=u'李世民',
        desc=u'唐太宗李世民，陇西成纪人，祖籍陇西成纪或 赵郡隆庆，是唐朝第二位皇帝，627年9月4日－649年7月10日在位，年号贞观。他名字的意思是“济世安民”。他是杰出的军事家，在唐朝的建立与统一过程中立下赫赫战功发挥了决定性作用，爱好文学与书法，有墨宝传世。',
        color='yellow',
        size=8)
    item.pages.append(page)

    item2 = Item(name=u'李渊',
        desc=u'唐高祖李渊（566年1月13日—635年），字叔德，祖籍陇西成纪（今甘肃秦安），唐朝开国皇帝，杰出的政治家和战略家。李渊出身于北朝的关陇贵族，七岁袭封唐国公。隋末天下大乱时，李渊乘势从太原起兵，攻占长安。公元618年5月，李渊称帝，国号唐，定都长安，不久之后便统一了全国。玄武门之变后，李渊退位成为太上皇。贞观九年，李渊病逝。谥号太武皇帝，庙号高祖，葬在献陵。唐高宗上元元年（674年）八月，改上尊号为神尧皇帝。唐玄宗天宝十三载二月，上尊号神尧大圣大光孝皇帝。',
        color='yellow',
        size=6)
    item2.pages.append(page)

    item3 = Item(name=u'魏征',
        desc=u'魏徵（580年－643年2月11日），字玄成。汉族，唐巨鹿人（今河北邢台市巨鹿县人，又说河北晋州市或河北馆陶市）人，唐朝政治家。曾任谏议大夫、左光禄大夫，封郑国公，谥文贞，以直谏敢言著称，是中国史上最负盛名的谏臣。著有《隋书》序论，《梁书》、《陈书》、《齐书》的总论等。其言论多见《贞观政要》。其中最著名，并流传下来的谏文表---《谏太宗十思疏》。他的重要言论大都收录在唐时王方庆所编《魏郑公谏录》和吴兢所编《贞观政要》两书里。为凌烟阁二十四功之一。',
        color='green',
        size=1)
    item3.pages.append(page)

    item4 = Item(name=u'隋炀帝',
        desc=u'隋炀帝杨广（569年－618年4月11日），华阴人（今陕西华阴），生于隋京师长安，是隋朝第二代皇帝，唐朝谥炀皇帝，夏王窦建德谥闵皇帝，其孙杨侗谥为世祖明皇帝。一名英，小字阿麽。隋文帝杨坚、独孤皇后的次子，开皇元年（581年）立为晋王，开皇二十年（600年）十一月立为太子，仁寿四年（604年）七月继位。他在位期间修建大运河（开通永济渠、通济渠，加修邗沟、江南运河），营建东都迁都洛阳城，开创科举制度，亲征吐谷浑，三征高句丽，因为滥用民力，造成天下大乱直接导致了隋朝的灭亡，618年在江都被部下缢杀。《全隋诗》录存其诗40多首。',
        color='yellow',
        size=7)
    item4.pages.append(page)

    link = Link(desc=u'父子')
    link.size = 10
    link.item1 = item
    link.item2 = item2

    link2 = Link(desc=u'君臣')
    link2.size = 7
    link2.item1 = item
    link2.item2 = item3

    dbsession.add_all([page, page2, page3, item, item2, item3, item4, link, link2])
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


class AdminView(ModelView):
    form_overrides = dict(desc=CKTextAreaField)
    column_labels = dict(desc='Description')
    create_template = 'myform.html'
    edit_template = 'myform.html'
    list_template = 'mylist.html'
    form_excluded_columns = ['cre_date']

    def get_list(self, *args, **kwargs):
        count, data = super(AdminView, self).get_list(*args, **kwargs)
        for item in data:
            if hasattr(item, 'desc') and item.desc:
                item.desc = item.desc[0:40]

        return count, data


class PageAdminView(AdminView):
    column_list = ['title', 'desc', 'items', 'cre_date']
    form_excluded_columns = ['cre_date', 'items']
    column_searchable_list = ['title', 'desc']
    column_display_all_relations = True


class ItemAdminView(AdminView):
    column_list = ['name', 'desc', 'color', 'size', 'neighbors', 'pages', 'cre_date']
    column_searchable_list = ['name', 'desc']


class LinkAdminView(AdminView):
    column_list = ['item1', 'item2', 'desc', 'size', 'cre_date']
    column_searchable_list = ['desc']
    column_labels = dict(desc='Description', item1='Item', item2='Item')


admin = Admin(app, name='Linkind Admin')
admin.add_view(PageAdminView(Page, dbsession))
admin.add_view(ItemAdminView(Item, dbsession))
admin.add_view(LinkAdminView(Link, dbsession))

#####################################################################################
#
#                         Start App
#
#####################################################################################
app.debug = True
app.run('0.0.0.0', 8000)