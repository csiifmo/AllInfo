package application;

import javafx.application.Application;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;


public class  Main extends Application {
    FXMLLoader loader;

    public static void main(String[] args) throws Exception {
        launch(args);
    }

    @Override
    public void start(Stage stage) throws Exception {
        String fxmlFile = "/application/sample.fxml";
        loader = new FXMLLoader(this.getClass().getResource(fxmlFile));
        Parent root = loader.load();
        stage.setTitle("JavaFX and Maven");

        Scene scene = new Scene(root);
        scene.getStylesheets().add(getClass().getResource("/application/progress.css").toString());
        stage.setScene(scene);
        stage.show();
        stage.setResizable(false);
        stage.setOnCloseRequest(new EventHandler<WindowEvent>() {
            public void handle(WindowEvent we) {
                Controller controller = loader.getController();
                controller.close();
                System.exit(1);
            }
        });
    }
}


