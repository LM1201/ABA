#!/usr/bin/env python2


import plyj.parser as plyj

parser = plyj.Parser()
expr="""
   public void editTransaction(){
       Intent createTransactionIntent = new Intent(this.getApplicationContext(),FormActivity.class) ;
       createTransactionIntent.setAction(Intent.ACTION_INSERT_OR_EDIT) ;
       createTransactionIntent.putExtra(UxArgument.SELECTED_ACCOUNT_UID,mAccountUID) ;
      createTransactionIntent.putExtra(UxArgument.SELECTED_TRANSACTION_UID,mTransactionUID) ;
      createTransactionIntent.putExtra(UxArgument.FORM_TYPE,FormActivity.FormType.TRANSACTION_FORM.name()) ;
     startActivityForResult(createTransactionIntent,REQUEST_EDIT_TRANSACTION) ;
 }
"""
print(parser.parse_expression(expr))

