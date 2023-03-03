from flask import make_response

from project import db


class Bots(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, nullable=False)
    favorite = db.Column(db.Boolean, default=False)
    online = db.Column(db.Boolean, default=False)

    @staticmethod
    def create_bot(ip):
        try:
            if not Bots.query.filter_by(ip=ip).first():
                bot = Bots(ip=ip)
                db.session.add(bot)
                db.session.commit()
                return make_response('OK', 200)
            else:
                return make_response('Bot with this ip already exists', 300)
        except:
            return make_response('Error', 400)

    @staticmethod
    def get_all_bots():
        bots = Bots.query.order_by(Bots.id).all()
        return bots

    @staticmethod
    def get_bot_by_id(id):
        bot = Bots.query.filter_by(id=id).first()
        if bot:
            return bot
        return None

    @staticmethod
    def get_bots_by_ip(ip):
        bots = Bots.query.filter_by(ip=ip)
        if bots:
            return bots
        return make_response('Bot with this id not found', 404)

    @staticmethod
    def remove_bot_by_id(id):
        bot = Bots.query.filter_by(id=id).first()
        try:
            db.session.delete(bot)
            db.session.commit()
            return make_response('OK', 200)
        except:
            return make_response('Error', 400)

    @staticmethod
    def unfavorite_bot_by_id(id):
        bot = Bots.query.filter_by(id=id).first()
        try:
            bot.favorite = False
            db.session.commit()
            return make_response('OK', 200)
        except:
            return make_response('Error', 400)

    @staticmethod
    def favorite_bot_by_id(id):
        bot = Bots.query.filter_by(id=id).first()
        try:
            bot.favorite = True
            db.session.commit()
            return make_response('OK', 200)
        except:
            return make_response('Error', 400)

    def __repr__(self) -> str:
        return '<Bot %r>' % self.id


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return '<User %r>' % self.id
