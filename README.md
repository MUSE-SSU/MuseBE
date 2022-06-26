<div className = "readme">
<img width = "30%" src = "https://velog.velcdn.com/images/kt5680608/post/709d4791-3590-4086-bb2d-77f60c371dcf/image.jpg"/>
<img width = "30%" src = "https://velog.velcdn.com/images/kt5680608/post/04edc7eb-dd3b-49aa-ac11-5f2bbd61b61a/image.jpg">
<img width = "30%" src = "https://velog.velcdn.com/images/kt5680608/post/3e0b2ec5-c2a1-4939-8d6d-4c6e74ec98b7/image.jpg">
</div>

<hr>

# MUSE

### 소개

> MUSE는 하나의 주제에 대해서 사람에 따라 다양하게 표현될 수 있는 창의성에 대해 서로 공유하고 이를 통해 작가들의 영감을 고취하는 창작지원 서비스입니다.<br/>
> muse 바로가기 <a>https://muse.seoul.kr/</a>

### Architecture
<img width="1025" alt="Muse Architecture" src="https://user-images.githubusercontent.com/61671097/165908035-3d38c3e0-dc7b-4018-a875-4722853e079b.png">


### 기능 소개

#### 메인 페이지

> ![](https://velog.velcdn.com/images/kt5680608/post/03b2c7b8-e47c-4f30-a0bb-b0766b6ec995/image.gif)

#### 콘테스트 페이지

> ![](https://velog.velcdn.com/images/kt5680608/post/f2f72d05-f0f9-4a0f-970e-9bdfceff4112/image.gif)
>
> -   토글 버튼을 통해 이전 주차 게시물과 현재 주차 게시물을 볼 수 있습니다.

#### 레퍼런스 페이지

> ![](https://velog.velcdn.com/images/kt5680608/post/ca46691b-f57d-4b6d-abbb-54f572be0f65/image.gif)
>
> -   사진의 고유 크기를 최대한 유지하고자 Masonry Layout을 적용하였습니다.

#### MUSE페이지

> ![](https://velog.velcdn.com/images/kt5680608/post/251382a4-bec9-4853-a982-8a5a8ad416de/image.gif)
>
> -   다른 페이지와의 차별성을 두고 사진첩을 넘기는 느낌과 유사한 경험을 주고 싶어서 드래깅을 사용하였습니다.

#### 검색페이지

> ![](https://velog.velcdn.com/images/kt5680608/post/69af3d66-28ee-4fef-9459-c85eac61e7e0/image.gif)
>
> -   기본 검색과 더불어 가장 많은 태그가 달린 3개의 해시태그를 통해 검색할 수 있습니다.

#### 상세페이지

> ![](https://velog.velcdn.com/images/kt5680608/post/ea23e0d2-723c-4e83-a25f-6c280a60d888/image.gif)
>
> -   뒤로가기로 생기는 로딩을 최소화 하기 위해 Modal을 채용하였습니다.

#### 색상 검색

> ![](https://velog.velcdn.com/images/kt5680608/post/e28eb620-d33e-419a-932e-91a6abf8f5e1/image.gif)
>
> -   Weekly Colour는 매 주 올라온 게시물의 색상을 추출하여 이를 사용자에게 보여줍니다. 해당 색상을 클릭시 색상이 포함된 게시물 검색 페이지로 넘어가게 됩니다.
