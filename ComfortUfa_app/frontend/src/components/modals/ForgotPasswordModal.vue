<template>
    <Dialog
        :visible="visible"
        @update:visible="$emit('update:visible', $event)"
        modal
        header="Восстановление пароля"
        :style="{ width: '420px' }"
        :draggable="false"
        :closable="true"
        :dismissableMask="true"
        class="auth-dialog"
    >
        <div class="forgot-form">
            
            <!-- EMAIL -->
            <div class="form-group">
                <IftaLabel>
                    <i class="pi pi-envelope input-icon"></i>
                    <InputText 
                        v-model="email" 
                        type="email" 
                        variant="filled"
                        class="custom-input"
                    />
                    <label>Email</label>
                </IftaLabel>
            </div>

            <!-- CODE -->
            <div v-if="codeSent" class="form-group">
                <IftaLabel>
                    <i class="pi pi-key input-icon"></i>
                    <InputText 
                        v-model="codeInput" 
                        variant="filled"
                        class="custom-input"
                    />
                    <label>Код из email</label>
                </IftaLabel>
            </div>

            <!-- TIMER -->
            <div v-if="timer > 0" class="timer">
                ⏳ Осталось: {{ formattedTime }} сек
            </div>

            <Button
                v-if="!codeSent"
                label="Отправить код"
                class="w-full btn-send-code"
                :loading="sending"
                :disabled="sending"
                @click="sendCode"
            />

            <Button
                v-else
                label="Подтвердить"
                class="w-full btn-confirm-code"
                :loading="verifying"
                :disabled="verifying"
                @click="verifyCode"
            />

        </div>
    </Dialog>
</template>

<script>
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import IftaLabel from 'primevue/iftalabel'

export default {
    name: 'ForgotPasswordModal',
    components: { Dialog, InputText, Button, IftaLabel },
    props: { visible: Boolean },
    emits: ['update:visible'],
    data() {
        return {
            email: '',
            codeInput: '',
            generatedCode: '',
            codeSent: false,
            timer: 0,
            sending: false,
            verifying: false,
            interval: null
        }
    },
    computed: {
        formattedTime() {
            return this.timer.toString().padStart(3, '0')
        }
    },
    watch: {
        visible(newVal) {
            if (!newVal) {
                this.reset()
            }
        }
    },
    methods: {
        async sendCode() {
            if (!this.email) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Введите email',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
                return
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            if (!emailRegex.test(this.email)) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Введите корректный email',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
                return
            }

            this.sending = true
            try {
                // Имитация отправки
                await new Promise(resolve => setTimeout(resolve, 1000))
                
                this.generatedCode = Math.floor(100000 + Math.random() * 900000).toString()
                console.log('CODE:', this.generatedCode)

                this.codeSent = true
                this.timer = 300 // 5 минут

                this.interval = setInterval(() => {
                    this.timer--
                    if (this.timer <= 0) {
                        clearInterval(this.interval)
                        this.$toast.add({
                            severity: 'warn',
                            summary: 'Время вышло',
                            detail: 'Код больше не действителен',
                            life: 3000,
                            styleClass: 'my-big-toast'
                        })
                    }
                }, 1000)

                this.$toast.add({
                    severity: 'success',
                    summary: 'Успешно',
                    detail: `Код отправлен на ${this.email}`,
                    life: 3000,
                    styleClass: 'my-success-toast'
                })

            } catch (error) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось отправить код',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
            } finally {
                this.sending = false
            }
        },

        async verifyCode() {
            if (!this.codeInput) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Введите код',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
                return
            }

            if (this.timer <= 0) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Время действия кода истекло',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
                return
            }

            if (this.codeInput !== this.generatedCode) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Неверный код',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
                return
            }

            this.verifying = true
            try {
                // Имитация проверки
                await new Promise(resolve => setTimeout(resolve, 1000))

                this.$toast.add({
                    severity: 'success',
                    summary: 'Успешно',
                    detail: 'Пароль подтверждён! Можете ввести новый.',
                    life: 3000,
                    styleClass: 'my-success-toast'
                })

                // Сброс через 2 секунды
                setTimeout(() => {
                    this.$emit('update:visible', false)
                    this.reset()
                }, 2000)

            } catch (error) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Что-то пошло не так',
                    life: 3000,
                    styleClass: 'my-error-toast'
                })
            } finally {
                this.verifying = false
            }
        },

        reset() {
            this.email = ''
            this.codeInput = ''
            this.generatedCode = ''
            this.codeSent = false
            this.timer = 0
            if (this.interval) clearInterval(this.interval)
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
:deep(.p-iftalabel .p-inputtext) {
    padding-left: 2.5rem !important;
    width: 100%;
    height: 3.5rem;
    border-radius: 10px;
}

.form-group {
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
}

.custom-input {
    width: 100%;
}

.forgot-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.timer {
    text-align: center;
    color: #ef4444;
    font-weight: 600;
    padding: 12px;
    background: #fef2f2;
    border-radius: 8px;
    border: 1px solid #fecaca;
}

.btn-send-code,
.btn-confirm-code {
    margin-top: 10px;
    height: 3.5rem;
    border-radius: 10px !important;
    font-weight: 700 !important;
    border: none !important;
}

.btn-send-code {
    background: linear-gradient(135deg, #6b7280 0%, #374151 100%) !important;
}

.btn-confirm-code {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
}

/* Стили самого диалога */
:deep(.p-dialog) {
    border-radius: 18px !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
    border: none;
}

:deep(.p-dialog-header) {
    padding: 1.5rem 1.5rem 0 1.5rem !important;
}
</style>