// AwsConfig.java configura credenciales de AWS en la app
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.services.sns.SnsClient;
import software.amazon.awssdk.regions.Region;

@Configuration
public class AwsConfig {

    @Bean
    public SnsClient snsClient() {
        String accessKeyId = System.getenv("AWS_ACCESS_KEY_ID"); // TOMAR CREDENCIALES DEL SANDBOX
        String secretAccessKey = System.getenv("AWS_SECRET_ACCESS_KEY");  // TOMAR CREDENCIALES DEL SANDBOX
        String sessionToken = System.getenv("AWS_SESSION_TOKEN");  // TOMAR CREDENCIALES DEL SANDBOX

        AwsSessionCredentials sessionCredentials = AwsSessionCredentials.create(
                accessKeyId, secretAccessKey, sessionToken);

        return SnsClient.builder()
                .region(Region.US_EAST_1) // Cambia según la región de tus tópicos
                .credentialsProvider(StaticCredentialsProvider.create(sessionCredentials))
                .build();
    }
}















// SnsService.java: Se suscribe a TODOS los topicos del EDA
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.sns.SnsClient;
import software.amazon.awssdk.services.sns.model.SubscribeRequest;
import software.amazon.awssdk.services.sns.model.SubscribeResponse;
 
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
@Service
public class SnsSubscriptionService {
 
    private final SnsClient snsClient;
 
    public SnsSubscriptionService(SnsClient snsClient) {
        this.snsClient = snsClient;
    }
 
    public void subscribeToTopics(List<String> topicArns, String endpointUrl) {

		// Suscribe a todos los topicos
        for (String topicArn : topicArns) {
            SubscribeRequest request = SubscribeRequest.builder()
                    .protocol("https")
                    .endpoint(endpointUrl)
                    .topicArn(topicArn)
                    .build();
 
            try {
                SubscribeResponse response = snsClient.subscribe(request);
                System.out.println("suscrito al topico: " + topicArn + ", SubscriptionArn: " + response.subscriptionArn());
            } catch (Exception e) {
                System.err.println("Error suscribiendo al topico " + topicArn + ": " + e.getMessage());
            }
        }
    }
 
    // confirma la suscripcion tomando la suscription url enviada por AWS
    public void confirmSubscription(String subscribeUrl) throws IOException {
        HttpURLConnection connection = (HttpURLConnection) new URL(subscribeUrl).openConnection();
        connection.setRequestMethod("GET");
        int responseCode = connection.getResponseCode();
        System.out.println("codigo de respuesta de suscripcion: " + responseCode);
    }
}














// SnsController.java: endpoint HTTPS que gestiona los mensajes y suscipciones
import org.springframework.web.bind.annotation.*;
 
import java.util.Map;
@RestController
@RequestMapping("/sns-handler")
public class SnsController {
 
    private final SnsSubscriptionService subscriptionService;
 
    public SnsController(SnsSubscriptionService subscriptionService) {
        this.subscriptionService = subscriptionService;
    }
 
    @PostMapping
    public void handleSnsMessage(@RequestHeader("x-amz-sns-message-type") String messageType,
                                 @RequestBody Map<String, Object> snsMessage) throws Exception {
        if ("SubscriptionConfirmation".equalsIgnoreCase(messageType)) { // SI ES SUSCRIPCION; CONFIRMARLA
            String subscribeUrl = snsMessage.get("SubscribeURL").toString();
            System.out.println("Subscription confirmation URL: " + subscribeUrl);
            subscriptionService.confirmSubscription(subscribeUrl);
        } else if ("Notification".equalsIgnoreCase(messageType)) { // SI ES MENSAJE, PROCESARLO SEGUN LOGICA
            String topicArn = snsMessage.get("TopicArn").toString();
            String message = snsMessage.get("Message").toString();
 
            // Implementa lógica según el tópico
            System.out.println("Message from topic " + topicArn + ": " + message);
 
            // Ejemplo de lógica personalizada
            switch (topicArn) {
                case "arn:aws:sns:us-east-1:442042507897:artist-topic":
                    System.out.println("Handling artist-topic message");
                    break;
                case "arn:aws:sns:us-east-1:442042507897:recital-topic":
                    System.out.println("Handling recital-topic message");
                    break;
                default:
                    System.out.println("Unhandled topic: " + topicArn);
            }
        }
    }
}












// TopicService.java: obtiene todos los topicos del EDA al momento de ejecucion
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONObject;
@Service
public class TopicService {

    public List<String> getTopics() throws Exception {
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder()
                .url("https://edaapi.deliver.ar/v1/health")
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                JSONObject jsonResponse = new JSONObject(responseBody);
                JSONArray topics = jsonResponse.getJSONObject("resources").getJSONArray("topics");

                List<String> topicArns = new ArrayList<>();
                for (int i = 0; i < topics.length(); i++) {
                    topicArns.add(topics.getJSONObject(i).getString("TopicArn"));
                }
                return topicArns;
            } else {
                throw new Exception("Failed to fetch topics. HTTP Status: " + response.code());
            }
        }
    }
}












// Application.java
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.List;
@SpringBootApplication
public class SnsApplication implements CommandLineRunner {

    private final TopicService topicService;
    private final SnsSubscriptionService subscriptionService;

    public SnsApplication(TopicService topicService, SnsSubscriptionService subscriptionService) {
        this.topicService = topicService;
        this.subscriptionService = subscriptionService;
    }

    public static void main(String[] args) {
        SpringApplication.run(SnsApplication.class, args);
    }

    @Override
    public void run(String... args) throws Exception {
        List<String> topicArns = topicService.getTopics();
        subscriptionService.subscribeToTopics(topicArns, "https://tu-backend.com/sns-handler"); // Cambia al endpoint de tu backend
    }
}