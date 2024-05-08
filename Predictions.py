from tensorflow import keras
from tensorflow.keras import backend as K
import numpy as np

model_path = 'Insert the path to the model file here'

def predict_defect(img_path):
    model = keras.models.load_model(model_path)
    np.set_printoptions(suppress=True)
    img = keras.preprocessing.image.load_img(img_path, target_size=(224, 224))
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0 
    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(prediction[0])
    classes = ['folding marks', 'grain off', 'growth marks', 'loose grains', 'non defective', 'pinhole']
    class_label = classes[predicted_class_index]
    is_defective = class_label != 'non defective'
    K.clear_session() 
    return is_defective, class_label
