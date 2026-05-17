<!-- RegisterModal.vue -->
<template>
    <Dialog
        :visible="visible"
        @update:visible="$emit('update:visible', $event)"
        modal
        :style="{ width: '520px', maxWidth: '95vw', padding: '0px 20px 10px 20px' }"
        :draggable="false"
        :closable="true"
        :dismissableMask="true"
        class="auth-dialog"
    >
        <!-- HEADER -->
        <template #header>
            <div class="dialog-header">
                <div class="header-icon">
                    <i class="pi pi-user-plus"></i>
                </div>

                <div class="header-content">
                    <h2>Регистрация в ComfortUfa</h2>
                    <p>
                        Создайте аккаунт, чтобы оставлять отзывы и сохранять избранное
                    </p>
                </div>
            </div>
        </template>

        <form @submit.prevent="handleSubmit" class="register-form">

            <!-- Nickname -->
            <div class="form-group full">
                <IftaLabel class="full">
                    <i class="pi pi-user input-icon"></i>
                    <InputText
                        v-model="nickname"
                        class="full-input"
                        :class="{ 'p-invalid': submitted && !nickname }"
                        autocomplete="username"
                    />
                    <label>Никнейм *</label>
                </IftaLabel>
                <small v-if="submitted && !nickname" class="p-error">Введите никнейм</small>
            </div>

            <!-- Email -->
            <div class="form-group full">
                <IftaLabel class="full">
                    <i class="pi pi-envelope input-icon"></i>
                    <InputText
                        v-model="email"
                        type="email"
                        class="full-input"
                        :class="{ 'p-invalid': submitted && !email }"
                        autocomplete="email"
                    />
                    <label>Email *</label>
                </IftaLabel>

                <small v-if="submitted && !email" class="p-error">Введите email</small>
                <small v-else-if="email && !isValidEmail(email)" class="p-error">
                    Некорректный email
                </small>
            </div>

            <!-- Phone -->
            <div class="form-group full">
                <IftaLabel class="full">
                    <i class="pi pi-phone input-icon"></i>
                    <InputMask
                        v-model="phone"
                        mask="+7 (999) 999-99-99"
                        placeholder="+7 (___) ___-__-__"
                        class="full-input"
                        autocomplete="tel"
                    />
                    <label>Телефон</label>
                </IftaLabel>
            </div>

            <!-- Password -->
            <div class="form-group full">
                <IftaLabel class="full">
                    <i class="pi pi-lock input-icon"></i>
                    <Password
                        v-model="password"
                        toggleMask
                        :feedback="true"
                        class="full-input password-wrap"
                        inputClass="full-input-inner"
                        :class="{ 'p-invalid': submitted && !password }"
                        autocomplete="new-password"
                    />
                    <label>Пароль *</label>
                </IftaLabel>

                <small v-if="submitted && !password" class="p-error">
                    Введите пароль
                </small>
            </div>

            <!-- Confirm Password -->
            <div class="form-group full">
                <IftaLabel class="full">
                    <i class="pi pi-shield input-icon"></i>
                    <Password
                        v-model="confirmPassword"
                        :feedback="false"
                        toggleMask
                        class="full-input password-wrap"
                        inputClass="full-input-inner"
                        :class="{
                            'p-invalid':
                                submitted &&
                                password !== confirmPassword
                        }"
                        autocomplete="new-password"
                    />
                    <label>Повтор пароля *</label>
                </IftaLabel>

                <small
                    v-if="submitted && password !== confirmPassword"
                    class="p-error"
                >
                    Пароли не совпадают
                </small>
            </div>

            <!-- BUTTON -->
            <Button
                type="submit"
                label="Создать аккаунт"
                icon="pi pi-user-plus"
                class="btn-register"
                :loading="isLoading"
                :disabled="isLoading"
            />

            <!-- BACK TO LOGIN -->
            <div class="login-link">
                <Button
                    icon="pi pi-arrow-left"
                    label="Я уже зарегистрирован"
                    link
                    @click.prevent="$emit('switch-to-login')"
                    class="login-button"
                />
            </div>

        </form>
    </Dialog>
</template>

<script>
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import InputMask from 'primevue/inputmask'
import IftaLabel from 'primevue/iftalabel'
import api from '@/services/api'

export default {
    name: 'RegisterModal',
    components: {
        Dialog,
        InputText,
        Password,
        Button,
        InputMask,
        IftaLabel
    },
    props: {
        visible: Boolean,
        loading: Boolean
    },
    emits: ['update:visible', 'switch-to-login', 'register-success', 'register-error'],
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
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
        },

        async handleSubmit() {
            this.submitted = true
            
            // Валидация
            if (!this.nickname || !this.email || !this.password) {
                return
            }
            
            if (!this.isValidEmail(this.email)) {
                this.$emit('register-error', { message: 'Некорректный email' })
                return
            }
            
            if (this.password !== this.confirmPassword) {
                this.$emit('register-error', { message: 'Пароли не совпадают' })
                return
            }
            
            if (this.password.length < 6) {
                this.$emit('register-error', { message: 'Пароль должен быть не менее 6 символов' })
                return
            }
            
            // Отправка на сервер
            this.internalLoading = true
            
            try {
                const payload = {
                    email: this.email,
                    nickname: this.nickname,
                    phone: this.phone || null,
                    password: this.password
                }
                
                const response = await api.post('/api/auth/register', payload)
                
                // Успешная регистрация
                this.$emit('register-success', response.data)
                
                // Очистка формы
                this.nickname = ''
                this.email = ''
                this.phone = ''
                this.password = ''
                this.confirmPassword = ''
                this.submitted = false
                
            } catch (error) {
                console.error('[Register] Error:', error)
                const message = error.response?.data?.detail || 'Ошибка при регистрации'
                this.$emit('register-error', { message })
            } finally {
                this.internalLoading = false
            }
        }
    }
}
</script>

<style scoped>
/* ===== DIALOG HEADER FIX ===== */
:deep(.p-dialog-header) {
    padding: 0 !important;
    border-bottom: none !important;
}

.dialog-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.8rem 2.25rem 1.2rem;
}

/* ===== GREEN ICON BOX ===== */
.header-icon {
    width: 64px;
    height: 64px;
    min-width: 64px;

    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;

    background: linear-gradient(135deg, #78a881 0%, #003f1a 100%);
    color: #fff;
    font-size: 1.6rem;

    box-shadow: 0 12px 24px rgba(0, 63, 26, 0.25);
}

/* ===== TEXT ===== */
.header-content h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 800;
    color: #0f172a;
}

.header-content p {
    margin: 0.3rem 0 0;
    font-size: 0.9rem;
    color: #64748b;
}

/* ===== FORM ===== */
.register-form {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

/* ===== FULL WIDTH FIX ===== */
.full {
    width: 100%;
}

.full-input {
    width: 100% !important;
}

:deep(.p-iftalabel) {
    width: 100%;
    display: block;
}

:deep(.p-inputtext),
:deep(.p-password),
:deep(.p-inputmask) {
    width: 100% !important;
}

/* ===== ICON INSIDE INPUT ===== */
.input-icon {
    position: absolute;
    top: 1.75rem;
    left: 1rem;
    transform: translateY(-50%);
    color: #94a3b8;
}

/* ===== INPUT STYLE ===== */
:deep(.p-inputtext),
:deep(.p-password input),
:deep(.p-inputmask) {
    height: 3.6rem;
    padding-left: 2.7rem !important;
    border-radius: 14px !important;
    background: #f8fafc !important;
}

/* ===== BUTTON ===== */
.btn-register {
    width: 100%;
    height: 3.6rem;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #78a881, #003f1a) !important;
    font-weight: 700 !important;
}

/* ===== BACK LINK ===== */
.login-link {
    display: flex;
    justify-content: center;
    margin-top: 0.8rem;
    padding-top: 1.2rem;
    border-top: 1px solid #eee;
}

:deep(.login-button.p-button-link) {
    color: #0f7a2e !important;
    font-weight: 600;
}
</style>