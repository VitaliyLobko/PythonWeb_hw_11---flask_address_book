from sqlalchemy import and_
from src import db
from src import models
from src.libs.file_service import move_user_pic, delete_user_pic


def get_contacts_user(user_id):
    return db.session.query(models.Contact).filter(models.Contact.user_id == user_id).order_by(
        models.Contact.fullname).all()


def get_contact_user(contact_id, user_id):
    return db.session.query(models.Contact).filter(
        and_(models.Contact.user_id == user_id, models.Contact.id == contact_id)).one()


def update_contact(pic_id, user_id, fullname, email, phone, description):
    contact = get_contact_user(pic_id, user_id)
    contact.fullname = fullname
    contact.email = email
    contact.phone = phone
    contact.description = description
    db.session.commit()


def delete_contact(contact_id, user_id):
    contact = get_contact_user(contact_id, user_id)
    db.session.query(models.Contact).filter(
        and_(models.Contact.user_id == user_id, models.Contact.id == contact_id)).delete()
    delete_user_pic(contact.path)
    db.session.commit()


def upload_contact_for_user(user_id, file_path, fullname, phone, email, description):
    # user = find_by_id(user_id)
    filename, size = move_user_pic(user_id, file_path)
    contact = models.Contact(fullname=fullname, email=email, phone=phone, description=description, user_id=user_id,
                             path=filename, size=size)
    db.session.add(contact)
    db.session.commit()
