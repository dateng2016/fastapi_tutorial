from typing import List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# @router.get("/", response_model=List[schemas.Post])
# @router.get("/", response_model=List[schemas.PostOut])
@router.get("/")
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):
    # cursor.execute('''SELECT * FROM posts''')
    # posts = cursor.fetchall()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # posts = db.query(models.Post).filter(models.Post.owner_id==current_user.id).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id==models.Post.id, isouter=True).\
        group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results

# @app.get("/posts/{id}")
# def get_post(id: int):
#     cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
#     post = cursor.fetchone()
#     print(post)
#     return {"post_detail": post} 

# @router.get("/{id}", response_model=schemas.PostOut)
@router.get("/{id}") #, response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id==id).first()
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not Authorized to Perfrorm Requested Action")
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).\
        join(models.Vote, models.Vote.post_id==models.Post.id, isouter=True).\
        group_by(models.Post.id).filter(models.Post.id==id).first()


    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), 
                 current_user: schemas.UserOut = Depends(oauth2.get_current_user)):
    # print(f'This is the id from the authentication process: {user_id} and the type of it is {type(user_id)}')
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)


    # new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    # db.add(new_post)
    # # db.flush()
    # if new_post.content != 'hello world':
    #     # db.rollback()
    #     raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    # else:
    #     db.commit()


    

    return new_post

# def create_posts(post: Post):
#     cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s ) RETURNING *""", (post.title, post.content, post.published))
#     new_post = cursor.fetchone()
#     conn.commit()
#     return {"data": new_post}



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not Authorized to Perfrorm Requested Action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
#     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
#     deleted_post = cursor.fetchone()
#     conn.commit()
#     if deleted_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'post with id = {id} does not exist')
#     return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, 
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    # post_query.update({"title":"This is my updated title","content": "updated content"}, synchronize_session=False)
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not Authorized to Perfrorm Requested Action")

    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()


# @app.put("/posts/{id}")
# def update_post(id: int, post:Post):
#     cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
#     updated_post = cursor.fetchone()
#     conn.commit()
#     if updated_post == None: 
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'post with id = {id} does not exist')
#     return {"data": updated_post}
