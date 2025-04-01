<template>
  <div class="app-container">
    <h1 >Busca de Operadoras de Saúde</h1>

    <div class="search-box">
      <input
        v-model="searchTerm"
        @input="onSearch"
        placeholder="Digite CNPJ, razão social ou cidade..."
      />
      <span v-if="loading" class="loading-icon">🔍</span>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="resultados && resultados.length > 0" class="results">
      <div class="summary">
        {{ resultados.length }} resultado(s) para "{{ searchTerm }}"
      </div>

      <div v-for="(item, index) in resultados" :key="index" class="card">
        <h2>{{ item.Razao_Social || 'Nome não disponível' }}</h2>
        <p v-if="item.Nome_Fantasia"><strong>Nome Fantasia:</strong> {{ item.Nome_Fantasia }}</p>

        <div class="card-grid">
          <div>
            <strong>CNPJ:</strong> {{ formatCNPJ(item.CNPJ) }}<br>
            <strong>Registro ANS:</strong> {{ item.Registro_ANS || 'Não informado' }}
          </div>
          <div>
            <strong>Endereço:</strong>
            {{ item.Logradouro || '' }} {{ item.Numero || '' }}<br>
            {{ item.Cidade || '' }}/{{ item.UF || '' }} - CEP: {{ formatCEP(item.CEP) }}
          </div>
        </div>

        <div v-if="item.Telefone" class="contact">
          <strong>Contato:</strong>
          <span v-if="item.DDD">({{ item.DDD }}) </span>
          {{ formatTelefone(item.Telefone.toString()) }}
          <span v-if="item.Endereco_eletronico"> | Email: {{ item.Endereco_eletronico }}</span>
        </div>
      </div>
    </div>

    <div v-else-if="searchTerm && !loading" class="no-results">
      Nenhum resultado encontrado para "{{ searchTerm }}"
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      searchTerm: '',
      resultados: [], // Inicializado como array vazio
      loading: false,
      error: null
    }
  },
  methods: {
    async onSearch() {
      if (this.searchTerm.length < 2) {
        this.resultados = [];
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        const response = await axios.get('http://localhost:5000/buscar', {
          params: { termo: this.searchTerm }
        });

        // Garante que resultados seja sempre um array
        this.resultados = response.data?.resultados || [];

      } catch (err) {
        console.error("Erro na busca:", err);
        this.error = err.response?.data?.error || 'Erro ao buscar dados';
        this.resultados = [];
      } finally {
        this.loading = false;
      }
    },
    formatCNPJ(cnpj) {
      if (!cnpj) return 'Não informado';
      return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    },
    formatCEP(cep) {
      if (!cep) return 'Não informado';
      return cep.replace(/(\d{5})(\d{3})/, '$1-$2');
    },
    formatTelefone(tel) {
      if (!tel) return '';
      const num = tel.replace(/\D/g, '');
      if (num.length === 8) return num.replace(/(\d{4})(\d{4})/, '$1-$2');
      if (num.length === 9) return num.replace(/(\d{5})(\d{4})/, '$1-$2');
      return tel;
    }
  }
}
</script>

<style>

.tutulo{
  position: absolute;
  color: #000000;
}



.app-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #fcfcfc;
}

.search-box {
  position: relative;
  margin: 25px 0;
}

.search-box input {
  width: 100%;
  padding: 12px 20px;
  font-size: 16px;
  border: 2px solid #46f00d;
  border-radius: 8px;
  box-sizing: border-box;
}

.loading-icon {
  position: absolute;
  right: 15px;
  top: 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
}



.card {
  background: rgb(0, 0, 0);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 15px;
}

.card h2 {
  margin: 0 0 10px 0;
  color: #fcfcfc;
}

.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin: 15px 0;
}

.contact {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #000000;
}

.no-results {
  text-align: center;
  padding: 30px;
  color: #666;
  font-size: 1.1em;
}

@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
