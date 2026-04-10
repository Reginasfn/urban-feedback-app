<template>
    <Dialog
        :visible="visible"
        @update:visible="$emit('update:visible', $event)"
        modal
        header="Вход в ComfortUfa"
        :style="{ width: '400px' }"
        :draggable="false"
        :closable="true"
        :dismissableMask="true"
        class="auth-dialog"
    >
        <form @submit.prevent="handleSubmit" class="login-form pt-4">
            
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
                :loading="loading"
                :disabled="loading"
            />

            <!-- Ссылка на регистрацию -->
            <div class="register-link">
                <span>Нет аккаунта?</span>
                <Button 
                    label="Зарегистрироваться" 
                    link 
                    @click.prevent="$emit('switch-to-register')" 
                    class="p-0 font-bold ml-1"
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
import IftaLabel from 'primevue/iftalabel'

export default {
    name: 'LoginModal',    components: { Dialog, InputText, Password, Button, IftaLabel },
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
    emits: ['update:visible', 'login', 'close', 'register', 'switch-to-register'],
    data() {
        return {
            localEmail: '',
            localPassword: ''
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
        handleSubmit() {
            this.$emit('login', { email: this.localEmail, password: this.localPassword })
        },
        resetForm() {
            this.localEmail = ''
            this.localPassword = ''
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
:deep(.p-iftalabel .p-password-input) {
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

/* Растягиваем блок пароля */
:deep(.password-input) {
    display: flex;
}

.btn-login {
    margin-top: 10px;
    width: 100%;
    height: 3.5rem;
    border-radius: 10px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #79cea5 0%, #003f1a 100%) !important;
    border: none !important;
}

.register-link {
    margin-top: 20px;
    text-align: center;
    font-size: 14px;
    color: #64748b;
    padding-top: 16px;
    border-top: 1px solid #f1f5f9;
}

/* Твой фирменный зеленый цвет для ссылки */
:deep(.p-button.p-button-link) {
    color: #168f04 !important;
    text-decoration: none;
}

:deep(.p-button.p-button-link:hover) {
    text-decoration: underline;
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