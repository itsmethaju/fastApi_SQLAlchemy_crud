from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel
from typing import List,Annotated
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine) # inite base database 

class ChoiceBase(BaseModel):
    choice_test:str
    is_correct : bool
    
class QuestionBase(BaseModel):
    question_text:str
    choices:List[ChoiceBase]
    
class Updat_choices(BaseModel):
    choices:List[ChoiceBase]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session,Depends(get_db)]# init db sesson

@app.get("/get_choices")
async def get_choices(question_id:int , db:db_dependency):
    responce = db.query(models.Choices).filter(models.Choices.question_id==question_id).all()
    if not responce:
        raise HTTPException(status_code = 404,detail = "question ID or choices not found")
    else:
        return responce

@app.get("/get_question")
async def get_question(question_id:int , db:db_dependency):
    responce = db.query(models.Question).filter(models.Question.id==question_id).first()
    if not responce:
        raise HTTPException(status_code=404,detail="question not found")
    else:
        return responce

@app.post("/create_question/")
async def create_questions(question:QuestionBase, db: db_dependency):
    db_question = models.Question(question_text = question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    for choice in question.choices:
        db_choice = models.Choices(choice_test = choice.choice_test,is_correct=choice.is_correct,question_id = db_question.id)
        db.add(db_choice)
    db.commit()
    
@app.post("/update_question")
async def update_question(id:int,new_question:str,db:db_dependency):
    update = db.query(models.Question).filter(models.Question.id ==id).first()
    
    update.question_text = new_question
    db.commit()
    db.refresh(update)
    
    return {"success": True, "updated_question": update}
@app.post("/add_choice")
async def add_choice(id: int, choices: Updat_choices, db: db_dependency):
    # update = db.query(models.Question).filter(models.Question.id ==id).first()

    choice_to_update = db.query(models.Choices).filter(models.Choices.question_id == id).first()

    
    if choice_to_update is not None:
 
        for choice in choices.choices:
            db_choice = models.Choices(choice_test = choice.choice_test,is_correct=choice.is_correct,question_id = id)
            db.add(db_choice)
        db.commit()
        return {"success": True, "updated_choice": choices}
    else:
        print("no data found") 

        
    return HTTPException(status_code=404,detail="update")

@app.post("/update_choice")
async def update_choice(id:str,choice_test:str,is_correct:bool,db:db_dependency):
    data = db.query(models.Choices).filter(models.Choices.id == id).first()
    
    if not data:
        raise HTTPException(status_code=404,detail="chois id not found")
    data.choice_test = choice_test
    data.is_correct = is_correct
    db.commit()
    db.refresh(data)
    
    return {"status_code":200,"detial":data} 

@app.get("/question_and_choice")
async def get_choice_and_question(question_id:int,db:db_dependency):
    question = db.query(models.Question).filter(models.Question.id==question_id).first()
    choices = db.query(models.Choices).filter(models.Choices.question_id==question_id).all()
    
    if not question:
        raise HTTPException(status_code=404,detail="question Not Found")
    return question,choices



@app.delete("/delete_question")
async def delete_question(id:str,db:db_dependency):
    question = db.query(models.Question).filter(models.Question.id==id).first()
    
    if not question:
        raise HTTPException(status_code=404,detail="question not found")
    
    db.query(models.Choices).filter(models.Choices.question_id == id).delete()
    
    db.delete(question)
    db.commit()
    
    return {"status":200,"message": f"Question with id {id} and its choices have been deleted"}

@app.delete("/delete_choice")
async def delete_choice(id:str,db:db_dependency):
    choice = db.query(models.Choices).filter(models.Choices.id==id).first()
    
    if not choice:
        raise HTTPException(status_code=404,detail="choice not found")
    
    db.delete(choice)
    db.commit()
    
    return {"sucess":True,"message":f"choice id {id} is deleted"}