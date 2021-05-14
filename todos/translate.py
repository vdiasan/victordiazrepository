import os
import json
import logging
import boto3
from todos import decimalencoder


dynamodb = boto3.resource('dynamodb')
aws_translate = boto3.client('translate')
aws_comprehend = boto3.client('comprehend')


def translate(event, context):

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )
    print('::Result: '+str(result))
                        
    if not 'Item' in result:
        print('::Translate Failed')
        logging.error("Translate Failed")
        raise Exception("Couldn't find the todo item.")
        return
                                                            
    try:

        # get 'text' field to translate from todo
        text_to_translate = result['Item']['text']
        print('text_to_translate: ' + text_to_translate)
                                                                                            
        # determines the dominant language of the field 'text' from todo.
        dominant_language = aws_comprehend.detect_dominant_language(
              Text=text_to_translate
        )
        print('dominant_language: ' + str(dominant_language))
        source_language_code = dominant_language['Languages'][0]['LanguageCode']
        print('source_language_code: ' + str(source_language_code))    
                                                                                                                                        
        # get target language from path parameters ../{id}/{language_code}
        target_language_code = event['pathParameters']['language']
        print('target_language_code: ' + str(target_language_code))        
                                                                                                                                                                    
        # translate 'text' field from 'source' to 'target' lang code
        result_txt = aws_translate.translate_text(Text=text_to_translate, SourceLanguageCode=source_language_code, TargetLanguageCode=target_language_code)
        print("Translation output: " + str(result_txt))
        print("TranslatedText: " + str(result_txt['TranslatedText']))    
                                                                                                                                                                                              
        # change 'text' field value in a result var dictionary
        result['Item']['text'] = result_txt['TranslatedText']
                                                                                                                                                                                                                          
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Item'],
                               cls=decimalencoder.DecimalEncoder)
        }
                                                                                                                                                                                                                                                  
        return response

    except:
        print('::Translate Failed')
        logging.error("Translate Failed")
        raise Exception("Couldn't find the todo item.")
        return
