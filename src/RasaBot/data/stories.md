## story1
* greet 
  - utter_how_can_i_help 

* start 
  - utter_product_variety    
  - utter_product_query  

* show_product{"product":"camera"} 
  - action_product_search  
  - slot{"product": "camera"}
  - utter_feature_comparison_query 

* feature_comparison{"feature":"battery"} 
  - action_feature_comparison 
  - slot{"feature": "battery"}
  - utter_feature_comparison 

* feature_values{"feature_value":"7200"}
  - action_feature_values
  - slot{"feature_value":"7200"}
  - utter_comparisons_query

* comparisons{"comparison":"more than"} 
  - action_comparisons
  - slot{"asin": "1234567890"}
  - utter_feature_enquiry_query

* feature_enquiry{"feature":"battery"} 
  - utter_feature_enquiry 
  - action_feature_enquiry 
  - slot{"feature_value": "1050"}
  - utter_review_summary_query 

* review_summary{"rating":"summary of reviews"} 
  - utter_review_summary 
  - action_review_summary 
  - utter_review_sentiment_query

* review_sentiment{"review":"1 star reviews"} 
  - utter_review_sentiment 
  - action_review_sentiment 
  - utter_similar_products_query 

* similar_product{"similarity":"similar"} 
  - utter_similar_product 
  - action_similar_product 
  - utter_add_to_cart_query 

* add_to_cart 
  - utter_add_to_cart

* stop_shopping 
  - utter_stop_shopping

* goodbye 
  - utter_goodbye


