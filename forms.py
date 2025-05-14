from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class EngineerForm(FlaskForm):
    name = StringField('氏名', validators=[DataRequired(message='氏名は必須です')])
    department_id = SelectField('所属部署', coerce=int, validators=[DataRequired(message='所属部署は必須です')])
    submit = SubmitField('保存')

class ProductForm(FlaskForm):
    name = StringField('製品名', validators=[DataRequired(message='製品名は必須です')])
    vendor = StringField('ベンダー名', validators=[DataRequired(message='ベンダー名は必須です')])
    annual_inquiries = IntegerField('年間問い合わせ数', validators=[NumberRange(min=0, message='0以上の値を入力してください')], default=0)
    submit = SubmitField('保存')

class DepartmentForm(FlaskForm):
    name = StringField('部署名', validators=[DataRequired(message='部署名は必須です')])
    submit = SubmitField('保存')

class SettingsForm(FlaskForm):
    min_engineers_per_product = IntegerField('製品担当エンジニアの最小人数', 
                                           validators=[NumberRange(min=1, message='1以上の値を入力してください')], 
                                           default=2)
    max_products_per_engineer = IntegerField('エンジニアの担当製品数最大数', 
                                           validators=[NumberRange(min=1, message='1以上の値を入力してください')], 
                                           default=5)
    hours_per_inquiry = FloatField('問い合わせあたりの対応時間（時間）', 
                                 validators=[NumberRange(min=0.1, message='0.1以上の値を入力してください')], 
                                 default=1.0)
    inquiry_work_ratio = FloatField('総稼働に対する問い合わせ対応割合', 
                                  validators=[NumberRange(min=0.01, max=1.0, message='0.01から1.0の間で入力してください')], 
                                  default=0.6)
    work_hours_per_day = FloatField('1日あたりの稼働時間', 
                                  validators=[NumberRange(min=0.1, message='0.1以上の値を入力してください')], 
                                  default=7.5)
    work_days_per_year = IntegerField('年間稼働日数', 
                                    validators=[NumberRange(min=1, message='1以上の値を入力してください')], 
                                    default=240)
    submit = SubmitField('保存')

class SimulationForm(FlaskForm):
    name = StringField('シミュレーション名', validators=[DataRequired(message='シミュレーション名は必須です')])
    total_engineers_change = FloatField('総エンジニア数の変化率（％）', default=0.0)
    total_products_change = FloatField('総製品数の変化率（％）', default=0.0)
    annual_inquiries_change = FloatField('年間問い合わせ件数の変化率（％）', default=0.0)
    hours_per_inquiry_change = FloatField('問い合わせあたりの対応時間の変化率（％）', default=0.0)
    max_products_per_engineer_change = FloatField('エンジニアあたり製品数上限の変化率（％）', default=0.0)
    inquiry_work_ratio_change = FloatField('総稼働に対する問い合わせ対応割合の変化率（％）', default=0.0)
    submit = SubmitField('シミュレーション実行')
