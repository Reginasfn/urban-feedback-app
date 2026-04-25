<template>
    <Dialog
        :visible="visible"
        @update:visible="$emit('update:visible', $event)"
        modal
        header="Регистрация в ComfortUfa"
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
                    <InputText 
                        id="nickname" 
                        v-model="nickname" 
                        variant="filled" 
                        class="custom-input" 
                        :class="{ 'p-invalid': submitted && !nickname }"
                    />
                    <label for="nickname">Никнейм *</label>
                </IftaLabel>
                <small v-if="submitted && !nickname" class="p-error">Введите никнейм</small>
            </div>

            <!-- Email -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-envelope input-icon"></i>
                    <InputText 
                        id="email" 
                        v-model="email" 
                        type="email" 
                        variant="filled" 
                        class="custom-input" 
                        :class="{ 'p-invalid': submitted && !email }"
                    />
                    <label for="email">Email *</label>
                </IftaLabel>
                <small v-if="submitted && !email" class="p-error">Введите email</small>
                <small v-if="email && !isValidEmail(email)" class="p-error">Введите корректный email</small>
            </div>

            <!-- Телефон -->
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
                        :class="{ 'p-invalid': submitted && !password }"
                    >
                        <template #header>
                            <h6>Выберите пароль *</h6>
                        </template>
                        <template #footer>
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
                    <label for="password">Пароль *</label>
                </IftaLabel>
                <small v-if="submitted && !password" class="p-error">Введите пароль</small>
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
                        :class="{ 'p-invalid': submitted && password !== confirmPassword }"
                    />
                </IftaLabel>
                <small v-if="submitted && password !== confirmPassword" class="p-error">Пароли не совпадают</small>
            </div>

            <Button
                type="submit"
                label="Зарегистрироваться"
                icon="pi pi-user-plus"
                class="btn-register"
                :loading="loading"
                :disabled="loading"
            />

            <div class="login-link">
                <span>Уже есть аккаунт?</span>
                <Button 
                    label="Войти" 
                    link 
                    @click.prevent="$emit('switch-to-login')" 
                    class="p-0 font-bold ml-1" 
                />
            </div>

        </form>
    </Dialog>
</template>

<script>
import axios from 'axios'  // 👈 Импортируем axios
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
        visible: Boolean,
        loading: { type: Boolean, default: false }
    },
    emits: ['update:visible', 'register', 'switch-to-login', 'auth-success'],
    data() {
        return {
            nickname: '',
            email: '',
            phone: '',
            password: '',
            confirmPassword: '',
            submitted: false,
            internalLoading: false
        }
    },
    computed: {
        isLoading() {
            return this.loading || this.internalLoading
        }
    },
    methods: {
        isValidEmail(email) {
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            return regex.test(email)
        },
        async handleSubmit() {
            this.submitted = true
            
            // 🔍 Валидация
            if (!this.nickname.trim()) {
                this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Введите никнейм', life: 3000 })
                return
            }
            if (!this.email.trim() || !this.isValidEmail(this.email)) {
                this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Введите корректный email', life: 3000 })
                return
            }
            if (!this.password) {
                this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Введите пароль', life: 3000 })
                return
            }
            if (this.password !== this.confirmPassword) {
                this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Пароли не совпадают', life: 3000 })
                return
            }

            this.internalLoading = true

            try {
                // 👇 ЗАПРОС К БЭКЕНДУ
                const response = await axios.post('http://localhost:8000/api/auth/register', {
                    nickname: this.nickname.trim(),
                    email: this.email.trim(),
                    phone: this.phone || null,
                    password: this.password,
                    id_role: 1  // 👈 По умолчанию роль "пользователь"
                })

                // 🎉 Уведомление об успехе
                this.$toast?.add({
                    severity: 'success',
                    summary: 'Успешно',
                    detail: 'Аккаунт создан! Теперь вы можете войти.',
                    life: 3000,
                    styleClass: 'my-success-toast'
                })

                // 📡 Сообщаем родителю (опционально — можно сразу переключить на вход)
                this.$emit('register', {
                    user: {
                        id: response.data.id_user,
                        nickname: response.data.nickname,
                        email: response.data.email
                    }
                })

                window.dispatchEvent(new CustomEvent('stats-refresh'))
                
                // 🔄 Сброс и переключение на вход
                this.resetForm()
                this.$emit('switch-to-login')

            } catch (error) {
                console.error('Register error:', error)
                
                const message = error.response?.data?.detail || 'Не удалось создать аккаунт'
                
                this.$toast?.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: message,
                    life: 4000,
                    styleClass: 'my-error-toast'
                })
            } finally {
                this.internalLoading = false
                this.submitted = false
            }
        },
        resetForm() {
            this.nickname = ''
            this.email = ''
            this.phone = ''
            this.password = ''
            this.confirmPassword = ''
            this.submitted = false
        }
    }
}
</script>

<style scoped>
/* === ТВОИ СТИЛИ — НЕ ТРОГАЛ === */
.input-icon {
    position: absolute;
    top: 35px;
    left: 17px;
    transform: translateY(-50%);
    z-index: 10;
    color: #94a3b8;
    
}
:deep(.p-iftalabel .p-inputtext),
:deep(.p-iftalabel .p-password-input),
:deep(.p-iftalabel .p-inputmask) {
    padding-left: 2.5rem !important;
    width: 100%;
    height: 3.5rem;
    border-radius: 10px;
}
.form-group { margin-bottom: 20px; }
.custom-input { width: 100%; }
:deep(.password-input) { display: flex; }
.btn-register {
    margin-top: 10px;
    width: 100%;
    height: 3.5rem;
    border-radius: 10px;
    font-weight: 700;
    background: linear-gradient(135deg, #78a881 0%, #003f1a 100%) !important;
    border: none;
    font-family:monospace
}
.login-link {
    margin-top: 20px;
    text-align: center;
    font-size: 14px;
    color: #64748b;
    font-family:monospace;
}
.p-button-link { color: #168f04 !important; font-family:monospace;}
:deep(.p-dialog) {
    border-radius: 18px !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
    
}
:deep(.p-dialog-header) { padding: 1.5rem 1.5rem 0 1.5rem !important; }
.p-error {
    color: #ef4444 !important;
    font-size: 12px !important;
    margin-top: 4px !important;
    display: block;
}
</style>