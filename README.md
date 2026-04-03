<p>
  <img src="./assets/logo.png"/ width="150">
</p>
<h1> Collec </h1>

<div>
  
 **✨ A smarter way to organize your memories ✨<br><br>**
  Have you ever felt like organizing all those screenshots that pile up every day?<br>
  Collec is a dedicated screenshot organizer app that automatically categorizes your screenshots and helps you conveniently manage them by category.
  Organize your screenshots efficiently with a clean interface and AI technology, without the hassle of managing complex folders. <br><br>
  🚀 Now available in [Google playstore!](https://play.google.com/store/apps/details?id=com.collec.collecfe)
</div><br>

This repository contains the AI section of Collec code implementation. <br>
[**Jiyoon Jeon**](https://github.com/JuneJe0n) · [**Moon Jaewon**](https://github.com/lumiere-on) contributed to implementing the AI pipeline.

<h2> AI Pipeline </h2>


<h3> Task Definition</h3>
To design an effective screenshot organization system, we first collected real-world screenshots from team members and analyzed their distribution.

Through this analysis, we found that most screenshots can be grouped into the following 10 categories.  
Accordingly, our AI pipeline is designed to classify screenshots into these categories:

```
1. Shopping  
2. Place  
3. Animal  
4. Person  
5. Coupon (Gifticon)  
6. Chat (SMS, KakaoTalk, DM, etc.)  
7. Music
8. Document
9. Reservation
10. Others  
```

<h3>Pipeline Details </h3>

Deploying and maintaining a fully self-hosted AI model is financially challenging. Therefore, we decided to leverage external APIs instead of serving our own models.

However, no single public API supported our target task, **10 class screenshot classification**.  
To address this, we designed a **multi-stage pipeline that combines multiple APIs sequentially**.

The APIs we use were carefully selected based on task suitability  cost efficiency, performance, and compatibility within the overall pipeline.

<p><img src="./assets/pipeline.png"/ width="500"></p>


**📍 [Stage 1] Azure Image Tagging**  [🔗](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/concept-tagging-images  )<br>
In the first stage, we use Azure Image Tagging to extract semantic tags from the input screenshot.
The target categories to extract are:
```
Shopping
Place
Animal
Person
```

**Method**
Azure returns a list of tags with confidence scores for a given image:
```
{
   "tags":[
      {"name":"grass","confidence":0.9960},
      {"name":"outdoor","confidence":0.9956},
      {"name":"building","confidence":0.9893},
      {"name":"property","confidence":0.9853},
      {"name":"plant","confidence":0.9791},
      {"name":"sky","confidence":0.9764},
      {"name":"home","confidence":0.9732},
      {"name":"house","confidence":0.9726}
   ]
}
```

Through empirical analysis, we observed that certain categories consistently produce characteristic tags:
```
- Animal → animal, dog, cat, fluffy, etc.
- Place → building, outdoor, sky, etc.
- Person → person, face, human, etc.
- Shopping → product, clothing, fashion, etc.
```

We predefine a tag set for each category, and apply rule-based matching:
- If the predicted tags intersect with a category-specific tag set → classify into that category
- Otherwise → pass the image to the next stage

This stage efficiently filters out a large portion of simple, visually distinguishable categories with minimal cost.











