<template>
    <Dialog
        :visible="visible"
        @update:visible="$emit('update:visible', $event)"
        modal
        header="Создать аккаунт ComfortUfa"
        :style="{ width: '450px' }"
        :draggable="false"
        :closable="true"
        :dismissableMask="true"
        class="auth-dialog"
    >
        <form @submit.prevent="handleSubmit" class="register-form pt-4">
            
            <!-- Nickname -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-user input-icon"></i>
                    <InputText id="nickname" v-model="nickname" variant="filled" class="custom-input" />
                    <label for="nickname">Никнейм</label>
                </IftaLabel>
            </div>

            <!-- Email -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-envelope input-icon"></i>
                    <InputText id="email" v-model="email" type="email" variant="filled" class="custom-input" />
                    <label for="email">Email</label>
                </IftaLabel>
            </div>

            <!-- Телефон (InputMask) -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-phone input-icon"></i>
                    <InputMask 
                        id="phone" 
                        v-model="phone" 
                        mask="+7 (999) 999-99-99" 
                        variant="filled" 
                        placeholder="+7 (___) ___-__-__"
                        class="custom-input" 
                    />
                    <label for="phone">Номер телефона</label>
                </IftaLabel>
            </div>

            <!-- Password -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-lock input-icon"></i>
                    <Password 
                        v-model="password" 
                        toggleMask 
                        variant="filled"
                        class="custom-input password-input"
                        inputClass="w-full"
                        promptLabel="Введите пароль"
                        weakLabel="Слабый"
                        mediumLabel="Средний"
                        strongLabel="Сильный"
                    >
                        <template #header>
                            <h6>Выберите пароль</h6>
                        </template>                        <template #footer>
                            <Divider />
                            <p class="mt-2 text-xs">Рекомендации:</p>
                            <ul class="pl-2 ml-2 mt-0 text-xs" style="line-height: 1.5">
                                <li>Хотя бы одна строчная буква</li>
                                <li>Хотя бы одна заглавная буква</li>
                                <li>Хотя бы одна цифра</li>
                                <li>Минимум 8 символов</li>
                            </ul>
                        </template>
                    </Password>
                    <label for="password">Пароль</label>
                </IftaLabel>
            </div>

            <!-- Confirm Password -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-shield input-icon"></i>
                    <Password 
                        v-model="confirmPassword" 
                        toggleMask 
                        :feedback="false" 
                        variant="filled"
                        class="custom-input password-input"
                        inputClass="w-full"
                    />
                    <label for="confirm-password">Повторите пароль</label>
                </IftaLabel>
            </div>

            <Button
                type="submit"
                label="Создать профиль"
                icon="pi pi-user-plus"
                class="btn-register"
            />

            <div class="login-link">
                <span>Уже есть аккаунт?</span>
                <Button label="Войти" link @click.prevent="$emit('switch-to-login')" class="p-0 font-bold ml-1" />
            </div>

        </form>
    </Dialog>
</template>

<script>
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import IftaLabel from 'primevue/iftalabel'
import InputMask from 'primevue/inputmask'
import Divider from 'primevue/divider'

export default {
    name: 'RegisterModal',
    components: { Dialog, InputText, Password, Button, IftaLabel, InputMask, Divider },
    props: {
        visible: Boolean
    },
    emits: ['update:visible', 'register', 'switch-to-login'],
    data() {
        return {
            nickname: '',
            email: '',
            phone: '',
            password: '',
            confirmPassword: ''
        }
    },
    methods: {
        handleSubmit() {
            if (this.password !== this.confirmPassword) {
                // Если у тебя подключен Toast, лучше вывести через него
                alert('Пароли не совпадают!')
                return
            }

            this.$emit('register', {
                nickname: this.nickname,
                email: this.email,
                phone: this.phone,
                password: this.password
            })
        }
    }
}
</script>

<style scoped>
/* Центрирование иконки в IftaLabel */
.input-icon {
    position: absolute;
    top: 50%;
    left: 12px;
    transform: translateY(-50%);
    z-index: 10;
    color: #94a3b8;
}

/* Кастомизация полей под иконку */
:deep(.p-iftalabel .p-inputtext),
:deep(.p-iftalabel .p-password-input),
:deep(.p-iftalabel .p-inputmask) {
    padding-left: 2.5rem !important;
    width: 100%;
    height: 3.5rem;
    border-radius: 10px;
}

.form-group {
    margin-bottom: 20px;
}

.custom-input {
    width: 100%;
}

/* Чтобы компонент пароля растягивался */
:deep(.password-input) {
    display: flex;
}

.btn-register {
    margin-top: 10px;
    width: 100%;
    height: 3.5rem;
    border-radius: 10px;
    font-weight: 700;
    background: linear-gradient(135deg, #79cea5 0%, #003f1a 100%) !important;
    border: none;
}

.login-link {
    margin-top: 20px;
    text-align: center;
    font-size: 14px;
    color: #64748b;
}

.p-button-link {
    color: #168f04 !important; /* Твой зеленый цвет */
}

/* Стиль диалога */
:deep(.p-dialog) {
    border-radius: 18px !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
}

:deep(.p-dialog-header) {
    padding: 1.5rem 1.5rem 0 1.5rem !important;
}
</style>