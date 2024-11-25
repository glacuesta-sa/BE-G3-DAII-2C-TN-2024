const AWS = require('aws-sdk');
const axios = require('axios');

// Configurar AWS SDK
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: 'us-east-1', // Cambia según la región de tus tópicos
});

// Crear instancia de SNS
const sns = new AWS.SNS();

async function subscribeToTopics() {
  try {
    // Obtener tópicos dinámicos desde el endpoint
    const response = await axios.get('https://edaapi.deliver.ar/v1/health');
    const topics = response.data?.resources?.topics;

    if (!topics || topics.length === 0) {
      console.error('No hay tópicos para suscribirse.');
      return;
    }

    const endpointUrl = 'https://tu-backend.com/sns-handler'; // Cambia al endpoint de tu backend

    for (const topic of topics) {
      const topicArn = topic.TopicArn;

      // Crear suscripción HTTPS
      const params = {
        Protocol: 'https', // Protocolo HTTPS
        TopicArn: topicArn,
        Endpoint: endpointUrl, // URL de tu endpoint HTTPS
      };

      try {
        const subscription = await sns.subscribe(params).promise();
        console.log(`Suscripción exitosa: ${subscription.SubscriptionArn} para el tópico: ${topicArn}`);
      } catch (err) {
        console.error(`Error suscribiéndose al tópico ${topicArn}:`, err.message);
      }
    }
  } catch (error) {
    console.error('Error obteniendo la lista de tópicos:', error.message);
  }
}

// Llama a la función para suscribirte
subscribeToTopics();

// Handler para recibir mensajes desde SNS
const express = require('express');
const app = express();
app.use(express.json());

app.post('/sns-handler', (req, res) => {
  const messageType = req.headers['x-amz-sns-message-type'];
  const message = req.body;

  if (messageType === 'SubscriptionConfirmation') {
    // Confirmar la suscripción
    axios
      .get(message.SubscribeURL)
      .then(() => console.log('Suscripción confirmada'))
      .catch((err) => console.error('Error confirmando suscripción:', err.message));
  } else if (messageType === 'Notification') {
    // Procesar notificaciones
    console.log(`Mensaje recibido del tópico ${message.TopicArn}:`, message.Message);

    // Implementar lógica específica según el tópico
    switch (message.TopicArn) {
      case 'arn:aws:sns:us-east-1:442042507897:artist-topic':
        // Lógica para artist-topic
        break;
      case 'arn:aws:sns:us-east-1:442042507897:recital-topic':
        // Lógica para recital-topic
        break;
      // Agregar más casos según sea necesario
      default:
        console.log('Mensaje de tópico desconocido:', message.TopicArn);
    }
  }

  res.sendStatus(200); // Responder a SNS
});

// Iniciar el servidor
app.listen(3000, () => {
  console.log('Servidor corriendo en el puerto 3000');
});