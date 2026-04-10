<template>
    <Dialog
        :visible="visible"
        @update:visible="$emit('update:visible', $event)"
        modal
        header="Вход в ComfortUfa"
        :style="{ width: '420px' }"
    >
        <form @submit.prevent="handleSubmit" class="login-form">
            
            <!-- Email -->
            <div class="form-group">
                <IftaLabel>
                    <InputText 
                        id="email" 
                        v-model="localEmail" 
                        type="email"
                        placeholder=" "
                        class="custom-input"
                    />
                    <label for="email">Email</label>
                </IftaLabel>
            </div>

            <!-- Password -->
            <div class="form-group">
                <IftaLabel>
                    <Password 
                        id="password"
                        v-model="localPassword" 
                        toggleMask 
                        placeholder=" "
                        class="custom-input"
                        :feedback="false"
                    />
                    <label for="password">Пароль</label>
                </IftaLabel>
            </div>

            <!-- Кнопка входа -->
            <Button 
                type="submit"
                label="Войти" 
                class="btn-login"
                :loading="loading"
                :disabled="loading"
            />

            <!-- Ссылка на регистрацию -->
            <div class="register-link">
                <span>Нет аккаунта?</span>
                <a @click.prevent="onRegisterClick">Зарегистрироваться</a>
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
    name: 'LoginModal',
    components: { Dialog, InputText, Password, Button, IftaLabel },
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
    emits: ['update:visible', 'login', 'close', 'register'],
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
        onClose() {
            this.$emit('update:visible', false)
            this.$emit('close')
        },
        onRegisterClick() {
            this.onClose()
            this.$emit('register')
        },
        resetForm() {
            this.localEmail = ''
            this.localPassword = ''
        }
    }
}
</script>

<style scoped>
/* Добавь стили из твоего AppHeader.vue для формы */
.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 16px;
}

.custom-input {
    width: 100%;
}

.btn-login {
    margin-top: 16px;
}

.register-link {
    text-align: center;
    font-size: 14px;
    color: #64748b;
    padding-top: 16px;
    border-top: 1px solid #e2e8f0;
}

.register-link a {
    color: #168f04;
    cursor: pointer;
    margin-left: 4px;
    font-weight: 600;
    text-decoration: none;
}

.register-link a:hover {
    color: #1e5f39;
    text-decoration: underline;
}
</style>