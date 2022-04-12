from .user import *
from typing import Optional
from random import randint

router = APIRouter(
    prefix='/discover',
    tags=['Match Making!']
)


@router.get('/', status_code=200, description="Discover new people!", response_model=List[schemas.UserDetailsFilter])
async def discover_people(first_name: Optional[str] = None,
                          last_name: Optional[str] = None,
                          age: Optional[str] = None,
                          gender: Optional[str] = None,
                          sexuality: Optional[str] = None,
                          passions: Optional[str] = None,
                          profession: Optional[str] = None,
                          db: Session = Depends(get_db),
                          user: schemas.User = Depends(get_current_user)):

    query = db.query(models.UserDetails)

    if first_name:
        query = query.filter(models.UserDetails.first_name == first_name)

    if last_name:
        query = query.filter(models.UserDetails.last_name == last_name)

    if age:
        query = query.filter(models.UserDetails.age == age)

    if gender:
        query = query.filter(models.UserDetails.gender == gender)

    if sexuality:
        query = query.filter(models.UserDetails.sexuality == sexuality)

    if passions:
        query = query.filter(models.UserDetails.passions == passions)

    if profession:
        query = query.filter(models.UserDetails.profession == profession)

    return query.all()


@router.get('/likes/{id}', status_code=200, description="User Likes!", response_model=schemas.UserLikedFilter)
async def get_liked_users(id,
                          db: Session = Depends(get_db),
                          user: schemas.User = Depends(get_current_user)):
    query = db.query(models.User).filter(models.User.id == id).first()

    if query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found!")

    return query


@router.get('/top', status_code=200, description="Top Picks", response_model=List[schemas.ShowIdUser])
async def show_top_picks(likes_count: Optional[int] = None,
                         db: Session = Depends(get_db),
                         user: schemas.User = Depends(get_current_user)):
    query = db.query(models.User).order_by('likes_count')

    if likes_count:
        query = query.filter(models.User.likes_count == likes_count)

    return query.all()


@router.get('/likelist/{id}', status_code=200, response_model=schemas.Likes)
async def show_likeslist(id,
                         db: Session = Depends(get_db),
                         user: schemas.User = Depends(get_current_user)):

    object = db.query(models.User).filter(
        models.User.id == id).first()
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} not found")
    await asyncio.sleep(0.5)
    return object


@router.get('/match', status_code=200)
async def get_matched(db: Session = Depends(get_db),
                      user: schemas.User = Depends(get_current_user)):
    query = db.query(models.UserDetails)

    useR = db.query(models.User).filter(
        models.User.id == user['user_id']).first()
    liked = list(useR.likes)

    user_details = db.query(models.UserDetails).filter(
        models.UserDetails.user_id == user['user_id']).first()

    if user_details is None:
        raise HTTPException(status_code=404, detail="User Details Not Found!")

    content = ['age', 'profession', 'hobbies', 'passions', 'like']

    criteriaLen = len(content)
    c = randint(0, criteriaLen - 1)
    query_parms = content[c]

    if query_parms == 'age':
        query = query.filter(models.UserDetails.age == user_details.age)

    elif query_parms == 'profession':
        query = query.filter(
            models.UserDetails.profession == user_details.profession)

    elif query_parms == 'hobbies':
        query = query.filter(
            models.UserDetails.hobbies == user_details.hobbies)

    elif query_parms == 'passions':
        query = query.filter(
            models.UserDetails.passions == user_details.passions)

    elif query_parms == 'like':
        query = query.filter(models.User.id in liked)

    else:
        query = query

    count = query.count()

    try:
        random_choice = randint(0, count - 1)
    except:
        random_choice = 0

    if count != 0:
        matched_user = query.all()[random_choice]
    else:
        return {"error": "Couldn't find, Please try again!"}

    return {
        "Detail": "You're matched!",
        "user_id": matched_user.user_id
    }
