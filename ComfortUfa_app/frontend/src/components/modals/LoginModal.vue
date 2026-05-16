<!-- LoginModal.vue -->
<template>
    <Dialog
        :visible="visible"
        @update:visible="$emit('update:visible', $event)"
        modal
        header="Вход в ComfortUfa"
        :style="{ width: '440px', maxWidth: '95vw', padding: '30px' }"
        :draggable="false"
        :closable="true"
        :dismissableMask="true"
        class="auth-dialog"
    >
        <template #header>
            <div class="dialog-header">
                <div class="header-icon">
                    <i class="pi pi-user"></i>
                </div>
                <div class="header-content">
                    <h2>Вход в ComfortUfa</h2>
                    <p>
                        Авторизуйтесь, чтобы оставлять отзывы и сохранять
                        избранные места
                    </p>
                </div>
            </div>
        </template>

        <form @submit.prevent="handleSubmit" class="login-form">
            <!-- Email -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-envelope input-icon"></i>
                    <InputText
                        id="email"
                        v-model="localEmail"
                        type="email"
                        variant="filled"
                        class="custom-input"
                    />
                    <label for="email">Email</label>
                </IftaLabel>
            </div>

            <!-- Password -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-lock input-icon"></i>
                    <Password
                        id="password"
                        v-model="localPassword"
                        toggleMask
                        :feedback="false"
                        variant="filled"
                        class="custom-input password-input"
                        inputClass="w-full"
                    />
                    <label for="password">Пароль</label>
                </IftaLabel>
            </div>

            <!-- Кнопка входа -->
            <Button
                type="submit"
                label="Войти"
                icon="pi pi-sign-in"
                class="btn-login"
                :loading="isLoading"
                :disabled="isLoading"
            />

            <!-- Ссылка на регистрацию -->
            <div class="register-link">
                <span>Нет аккаунта?</span>
                <Button
                    label="Зарегистрироваться"
                    link
                    @click.prevent="$emit('switch-to-register')"
                    class="register-button"
                />
            </div>
        </form>
    </Dialog>
</template>

<script>
import axios from 'axios'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import IftaLabel from 'primevue/iftalabel'

export default {
    name: 'LoginModal',
    components: {
        Dialog,
        InputText,
        Password,
        Button,
        IftaLabel
    },
    props: {
        visible: {
            type: Boolean,
            required: true
        },
        loading: {
            type: Boolean,
            default: false
        }
    },
    emits: [
        'update:visible',
        'login',
        'close',
        'register',
        'switch-to-register',
        'auth-success'
    ],
    data() {
        return {
            localEmail: '',
            localPassword: '',
            internalLoading: false
        }
    },
    computed: {
        isLoading() {
            return this.loading || this.internalLoading
        }
    },
    watch: {
        visible(newVal) {
            if (!newVal) {
                this.resetForm()
            }
        }
    },
    methods: {
        async handleSubmit() {
            if (!this.localEmail || !this.localPassword) {
                this.$toast?.add({
                    severity: 'warn',
                    summary: 'Заполните поля',
                    detail: 'Введите email и пароль',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
                return
            }

            this.internalLoading = true

            try {
                const response = await axios.post(
                    'http://localhost:8000/api/auth/login',
                    {
                        email: this.localEmail.trim(),
                        password: this.localPassword
                    }
                )

                localStorage.setItem(
                    'auth_token',
                    response.data.access_token
                )

                localStorage.setItem(
                    'user',
                    JSON.stringify({
                        id: response.data.user_id,
                        nickname: response.data.nickname,
                        role: response.data.role
                    })
                )

                this.$toast?.add({
                    severity: 'success',
                    summary: 'Успешно',
                    detail: `Добро пожаловать, ${response.data.nickname}!`,
                    life: 3000,
                    styleClass: 'my-success-toast'
                })

                this.$emit('login', {
                    email: this.localEmail,
                    password: this.localPassword,
                    response: response.data
                })

                window.dispatchEvent(new CustomEvent('stats-refresh'))

                this.$emit('update:visible', false)
                this.resetForm()
            } catch (error) {
                console.error('Login error:', error)

                const message =
                    error.response?.data?.detail ||
                    'Ошибка входа. Проверьте данные.'

                this.$toast?.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: message,
                    life: 4000,
                    styleClass: 'my-big-toast'
                })
            } finally {
                this.internalLoading = false
            }
        },

        resetForm() {
            this.localEmail = ''
            this.localPassword = ''
        }
    }
}
</script>

<style scoped>
/* ========================================
   ДИАЛОГ
======================================== */
:deep(.p-dialog) {
    border: none !important;
    border-radius: 28px !important;
    overflow: hidden !important;
    background: #ffffff !important;
    box-shadow:
        0 30px 60px rgba(15, 23, 42, 0.18),
        0 12px 24px rgba(15, 23, 42, 0.08) !important;
}

:deep(.p-dialog-header) {
    padding: 0 2.25rem !important;
    border: none !important;
    background:
        radial-gradient(circle at top right, rgba(120, 168, 129, 0.25), transparent 45%),
        linear-gradient(135deg, #f8fafc 0%, #eef7f0 100%) !important;
}

:deep(.p-dialog-content) {
    padding: 2rem 2.25rem 2.25rem 2.25rem !important;
    background: #ffffff !important;
}

:deep(.p-dialog-header-icon) {
    width: 2.5rem !important;
    height: 2.5rem !important;
    border-radius: 50% !important;
    background: rgba(255, 255, 255, 0.9) !important;
    color: #334155 !important;
    transition: all 0.2s ease;
}

:deep(.p-dialog-header-icon:hover) {
    background: #ffffff !important;
    transform: scale(1.05);
}

/* ========================================
   HEADER
======================================== */
.dialog-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    padding: 2rem 0 1.5rem;
}

.header-icon {
    width: 64px;
    height: 64px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #78a881 0%, #003f1a 100%);
    color: #ffffff;
    font-size: 1.6rem;
    box-shadow: 0 12px 24px rgba(0, 63, 26, 0.25);
    flex-shrink: 0;
}

.header-content {
    flex: 1;
}

.header-content h2 {
    margin: 0 0 0.35rem;
    font-size: 1.55rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
}

.header-content p {
    margin: 0;
    font-size: 0.92rem;
    color: #64748b;
    line-height: 1.5;
}

/* ========================================
   FORM
======================================== */
.login-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.form-group {
    position: relative;
}

.custom-input {
    width: 100%;
}

/* ========================================
   INPUTS
======================================== */
.input-icon {
    position: absolute;
    top: 1.75rem;
    left: 1rem;
    transform: translateY(-50%);
    z-index: 10;
    color: #94a3b8;
    font-size: 1rem;
}

:deep(.p-iftalabel) {
    width: 100%;
}

:deep(.p-iftalabel .p-inputtext),
:deep(.p-iftalabel .p-password-input) {
    width: 100% !important;
    height: 3.6rem;
    padding-left: 2.8rem !important;
    padding-right: 1rem !important;
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
    background: #f8fafc !important;
    box-shadow: none !important;
    transition: all 0.25s ease !important;
}

:deep(.p-iftalabel .p-inputtext:hover),
:deep(.p-iftalabel .p-password-input:hover) {
    border-color: #cbd5e1 !important;
    background: #ffffff !important;
}

:deep(.p-iftalabel .p-inputtext:focus),
:deep(.p-iftalabel .p-password-input:focus) {
    border-color: #78a881 !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 4px rgba(120, 168, 129, 0.15) !important;
}

:deep(.p-iftalabel label) {
    color: #64748b !important;
    font-weight: 500;
}

:deep(.password-input) {
    display: flex;
    width: 100%;
}

:deep(.p-password) {
    width: 100%;
}

:deep(.p-password-input) {
    width: 100%;
}

:deep(.p-password .p-password-toggle-mask-icon) {
    color: #94a3b8 !important;
}

/* ========================================
   КНОПКА ВХОДА
======================================== */
.btn-login {
    width: 100%;
    height: 3.6rem;
    margin-top: 0.5rem;
    border: none !important;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #78a881 0%, #003f1a 100%) !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.2px;
    box-shadow: 0 12px 24px rgba(0, 63, 26, 0.22);
    transition: all 0.25s ease !important;
}

.btn-login:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 16px 28px rgba(0, 63, 26, 0.28);
}

.btn-login:active:not(:disabled) {
    transform: translateY(0);
}

.btn-login:disabled {
    opacity: 0.75;
}

/* ========================================
   ССЫЛКА НА РЕГИСТРАЦИЮ
======================================== */
.register-link {
    margin-top: 0.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid #f1f5f9;
    text-align: center;
    font-size: 0.92rem;
    color: #64748b;
}

.register-button {
    padding: 0 !important;
    margin-left: 0.25rem;
}

:deep(.p-button.p-button-link) {
    color: #0f7a2e !important;
    font-weight: 700 !important;
    text-decoration: none !important;
}

:deep(.p-button.p-button-link:hover) {
    color: #065f23 !important;
    text-decoration: underline !important;
}

/* ========================================
   АДАПТИВНОСТЬ
======================================== */
@media (max-width: 576px) {
    .dialog-header {
        padding: 1.5rem 0 1.25rem;
        gap: 0.75rem;
    }

    .header-icon {
        width: 56px;
        height: 56px;
        font-size: 1.35rem;
        border-radius: 16px;
    }

    .header-content h2 {
        font-size: 1.3rem;
    }

    .header-content p {
        font-size: 0.85rem;
    }

    :deep(.p-dialog-header) {
        padding: 0 1.5rem !important;
    }

    :deep(.p-dialog-content) {
        padding: 1.5rem !important;
    }
}
</style>