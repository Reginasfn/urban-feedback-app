<template>
  <div class="about-simple">
    <h1 class="title">О проекте</h1>

    <div class="section">
      <p class="text">
        Это платформа для жителей Уфы, которые хотят влиять на состояние городской среды.
        Здесь можно отмечать объекты на карте — скамейки, фонари, детские площадки, кафе —
        и оставлять к ним отзывы: хвалить, предлагать улучшения или сообщать о проблемах.
      </p>
    </div>

    <div class="section">
      <h2 class="section-title"><i class="pi pi-question-circle"></i>Зачем это нужно?</h2>
      <p class="text">
        Город меняется каждый день, и только жители видят реальную картину.
        Официальные отчёты часто отстают от жизни, мы же даём возможность фиксировать
        изменения здесь и сейчас.
      </p>
    </div>

    <div class="section">
      <h2 class="section-title"><i class="pi pi-users"></i>Для кого этот проект?</h2>
      <p class="text">
        Для всех, кому небезразлична Уфа. Для жителей, которые хотят жить в комфортном дворе.
        Для активистов, которые собирают данные для обращений. Для представителей администрации,
        которым нужна обратная связь от горожан. Для исследователей, изучающих городскую среду.
      </p>
    </div>

    <div class="section">
      <h2 class="section-title"><i class="pi pi-map-marker"></i>Как это работает?</h2>
      <p class="text">
        Вы открываете карту, находите объект или же сами добавляете его, кликаете на него и оставляете отзыв.
        Это занимает меньше минуты. Все отзывы публикуются на карте — их видят другие
        пользователи и ответственные лица. Чем больше людей отмечают одну и ту же проблему,
        тем выше шанс, что её решат.
      </p>
    </div>

    <div class="section">
      <h2 class="section-title"><i class="pi pi-chart-bar"></i>Почему это важно?</h2>
      <p class="text">
        Изменения начинаются с малого. Одна жалоба на сломанный фонарь может
        остаться незамеченной. Если десять жителей отметят этот же объект — это уже
        статистика, с которой можно работать.
      </p>
    </div>

    <div class="section">
      <h2 class="section-title"><i class="pi pi-shield"></i>Что мы гарантируем?</h2>
      <p class="text">
        Открытость данных — вся информация доступна для просмотра. Модерацию без цензуры —
        удаляются только спам и оскорбления, но не критика. Фокус на действиях — отзывы
        структурированы так, чтобы по ним можно было реально работать.
      </p>
    </div>

    <p class="text highlight">
      <i class="pi pi-bullhorn"></i>
      Ваш голос имеет значение. Не ждите, пока кто-то другой заметит проблему.
      Сделайте это Вы — и помогите сделать Уфу комфортнее.
    </p>

    <router-link to="/map" class="link">
      Перейти к карте
      <i class="pi pi-arrow-right"></i>
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>

<style scoped>
.about-simple {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1a1a1a;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
  padding: 60px 20px 100px;
}

.title {
  font-size: 42px;
  font-weight: 900;
  color: rgb(0, 62, 5);
  text-transform: uppercase;
  margin: 0 0 40px 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.section {
  margin-bottom: 36px;
}

.section-title {
  font-size: 20px;
  font-weight: 800;
  color: rgb(0, 83, 40);
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-title .pi {
  font-size: 18px;
  color: #168f04;
  opacity: 0.8;
}

.text {
  font-size: 17px;
  color: #00540e;
  margin: 0 0 20px 0;
}

.text strong {
  font-weight: 700;
  color: rgb(0, 83, 40);
}

.highlight {
  background: rgba(22, 143, 4, 0.08);
  padding: 20px 24px;
  border-radius: 12px;
  border-left: 4px solid #168f04;
  font-weight: 600;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.highlight .pi {
  font-size: 16px;
  color: #168f04;
  margin-top: 3px;
  flex-shrink: 0;
}

.link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-top: 36px;
  font-size: 17px;
  font-weight: 700;
  color: #168f04;
  text-decoration: none;
  border: 2px solid #168f04;
  border-radius: 8px;
  padding: 14px 28px;
  transition: all 0.25s ease;
}

.link .pi {
  font-size: 14px;
  transition: transform 0.25s ease;
}

.link:hover {
  background: #168f04;
  color: white;
  box-shadow: 0 8px 20px rgba(22, 143, 4, 0.35);
}

.link:hover .pi {
  transform: translateX(4px);
}

@media (max-width: 768px) {
  .about-simple {
    padding: 100px 16px 40px;
  }

  .title {
    font-size: 32px;
  }

  .section-title {
    font-size: 18px;
  }

  .text {
    font-size: 16px;
  }

  .link {
    font-size: 16px;
    padding: 12px 24px;
  }
}
</style>