<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>
      <form @submit.prevent="$emit('save')" class="modal-form">
        <template v-if="entityType === 'employees'">
          <div class="form-group">
            <label>Nom:</label>
            <input v-model="form.name" type="text" required maxlength="100">
          </div>
          <div class="form-group">
            <label>Nom de Famille:</label>
            <input v-model="form.last_name" type="text" required maxlength="100">
          </div>
          <div class="form-group">
            <label>Rôle:</label>
            <select v-model="form.role_id" required>
              <option value="" disabled>Sélectionner un rôle</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Site de Construction:</label>
            <select v-model="form.construction_site_id" required>
              <option value="" disabled>Sélectionner un site</option>
              <option v-for="site in sites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Taux Horaire:</label>
            <input v-model="form.hourly_rate" type="number" required step="0.25" min="0">
          </div>
        </template>
        <template v-else-if="entityType === 'sites'">
          <div class="form-group">
            <label>Nom:</label>
            <input v-model="form.name" type="text" required maxlength="200">
          </div>
          <div class="form-group">
            <label>Adresse:</label>
            <textarea v-model="form.address" required maxlength="500" rows="3"></textarea>
          </div>
        </template>
        <template v-else-if="entityType === 'roles'">
          <div class="form-group">
            <label>Nom:</label>
            <input v-model="form.name" type="text" required maxlength="100">
          </div>
        </template>
        
        <div class="modal-actions">
          <button type="button" @click="$emit('close')" class="cancel-btn">Annuler</button>
          <button type="submit" :disabled="loading" class="save-btn">
            {{ buttonText }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModalComponent',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      required: true
    },
    entityType: {
      type: String,
      required: true
    },
    form: {
      type: Object,
      required: true
    },
    buttonText: {
      type: String,
      default: 'Créer'
    },
    loading: {
      type: Boolean,
      default: false
    },
    roles: {
      type: Array,
      default: () => []
    },
    sites: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'save']
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 500px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  letter-spacing: -0.025em;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: var(--space-sm);
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--error);
}

.modal-form {
  padding: var(--space-lg);
}

.form-group {
  margin-bottom: var(--space-lg);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: var(--space-md);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-family: inherit;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: none !important;
  outline: none !important;
}

.form-group select {
  width: 100%;
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-md);
  font-size: var(--text-sm);
  border-radius: var(--radius);
}


.form-group input:hover,
.form-group textarea:hover,
.form-group select:hover {
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
}

.cancel-btn:hover {
  background: var(--bg-primary);
}

.save-btn {
  background: var(--accent);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  cursor: pointer;
}

.save-btn:hover {
  background: var(--accent-hover);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>