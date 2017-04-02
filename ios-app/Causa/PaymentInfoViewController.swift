////
////  PaymentInfoViewController.swift
////  loveshare
////
////  Created by Pixnabi on 3/2/17.
////  Copyright © 2017 pixnabi. All rights reserved.
////
//
//import UIKit
//import Stripe
//import Parse
//import MBProgressHUD
//
//class PaymentInfoViewController: UIViewController {
//    
//    @IBOutlet weak var cardNameField: UITextField!
//    @IBOutlet weak var cardNumField: UITextField!
//    @IBOutlet weak var cardDateField: UITextField!
//    @IBOutlet weak var cardCodeField: UITextField!
//    @IBOutlet weak var checkView: UIImageView!
//    @IBOutlet weak var payBtn: UIButton!
//    @IBOutlet weak var cardinfoTitle: UILabel!
//    @IBOutlet weak var cancelBtn: UIButton!
//    @IBOutlet weak var saveCreditCardLabel: UILabel!
//    
//    let success = #imageLiteral(resourceName: "success")
//    var total = ""
//    var checkoutView: CheckoutViewController!
//    var company = ""
//    
//    var saveInfo = false {
//        didSet {
//            if saveInfo {
//                self.checkView.image = success
//            } else {
//                self.checkView.image = nil
//            }
//        }
//    }
//    
//    override func viewDidLoad() {
//        super.viewDidLoad()
//        NotificationCenter.default.addObserver(self, selector: #selector(self.receiveLanguageChangedNotification(notification:)), name: kNotificationLanguageChanged, object: nil)
//        self.configureViewFromLocalisation()
//        // Do any additional setup after loading the view.
//        self.view.backgroundColor = UIColor(red: 0, green: 0, blue: 0, alpha: 0.5)
//        self.checkView.layer.borderWidth = 1
//        self.checkView.layer.borderColor = UIColor.darkGray.cgColor
//        self.checkView.layer.cornerRadius = 25 / 2
//        self.checkView.clipsToBounds = true
//        self.payBtn.layer.cornerRadius = 20
//    }
//    
//    func configureViewFromLocalisation() {
//        print("configure language")
//        self.cardNameField.placeholder = Localization("CardName")
//        self.cardNumField.placeholder = Localization("CardNum")
//        self.cardinfoTitle.text = Localization("CardInfoTitle")
//        self.payBtn.setTitle(Localization("PayBtn"), for: .normal)
//        self.cancelBtn.setTitle(Localization("CancelBtn"), for: .normal)
//        self.saveCreditCardLabel.text = Localization("SaveCardCheck")
//    }
//    
//    func receiveLanguageChangedNotification(notification:NSNotification) {
//        if notification.name == kNotificationLanguageChanged {
//            configureViewFromLocalisation()
//        }
//    }
//    
//    @IBAction func saveCreditCardInfo(_ sender: UIButton) {
//        self.saveInfo = !saveInfo
//    }
//    
//    @IBAction func sendStripePayment(_ sender: UIButton) {
//        if let cardName = cardNameField.text,
//            let cardNum = cardNumField.text,
//            let cardDate = cardDateField.text,
//            let cvc = cardCodeField.text {
//            let cardParams = STPCardParams()
//            cardParams.name = cardName
//            cardParams.number = cardNum
//            cardParams.cvc = cvc
//            let dateArr = cardDate.components(separatedBy: "/")
//            if let month = UInt(dateArr[0]),
//                let year = UInt(dateArr[1]){
//                cardParams.expMonth = month
//                cardParams.expYear = year
//            }
//            
//            let indicator = MBProgressHUD.showAdded(to: self.view, animated: true)
//            STPAPIClient.shared().createToken(withCard: cardParams) { (token, error) in
//                if let err = error {
//                    indicator.hide(animated: true)
//                    let errDesc = err.localizedDescription
//                    Utils.showSimpleAlertWithTitle("", message: errDesc, viewController: self)
//                } else {
//                    if let token = token {
//                        print("got token: \(token)")
//                        if self.saveInfo {
//                            let params:[String:Any] = ["token":token.tokenId]
//                            print("User wants to save card info, so we using setCardToCustomer first")
//                            PFCloud.callFunction(inBackground: "setCardToCustomer", withParameters: params, block: { (response, error) in
//                                if let err = error {
//                                    indicator.hide(animated: true)
//                                    let errDesc = err.localizedDescription
//                                    Utils.showSimpleAlertWithTitle("", message: errDesc, viewController: self)
//                                } else {
//                                    if let _ = response {
//                                        let params:[String:Any] = ["price":self.total,
//                                                                   "company":self.company]
//                                        print("Card was succesfully saved to the user, now we finish the payment using sendStripePayment")
//                                        PFCloud.callFunction(inBackground: "sendStripePayment", withParameters: params, block: { (responser, error) in
//                                            indicator.hide(animated: true)
//                                            if let resp = response as? [String:Any] {
//                                                print("response: \(resp)")
//                                                self.dismiss(animated: true, completion: nil)
//                                                self.checkoutView.checkoutSuccess(response: resp)
//                                            } else {
//                                                if let err = error {
//                                                    let errDesc = err.localizedDescription
//                                                    Utils.showSimpleAlertWithTitle("", message: errDesc, viewController: self)
//                                                }
//                                            }
//                                        })
//                                    }
//                                }
//                            })
//                        } else {
//                            let params:[String:Any] = ["token":token.tokenId,
//                                                       "price":self.total,
//                                                       "company":self.company]
//                            
//                            PFCloud.callFunction(inBackground: "sendStripePaymentNoCard", withParameters: params, block: { (response, error) in
//                                indicator.hide(animated: true)
//                                if let err = error {
//                                    let errDesc = err.localizedDescription
//                                    Utils.showSimpleAlertWithTitle("", message: errDesc, viewController: self)
//                                } else {
//                                    if let resp = response as? [String:Any] {
//                                        print("response: \(resp)")
//                                        self.dismiss(animated: true, completion: nil)
//                                        self.checkoutView.checkoutSuccess(response: resp)
//                                    }
//                                }
//                            })
//                        }
//                    }
//                }
//            }
//        }
//    }
//    
//    @IBAction func cancelPayment(_ sender: UIButton) {
//        self.dismiss(animated: true, completion: nil)
//        sendAsGift = false
//        emailGift = ""
//    }
//}
//
//extension PaymentInfoViewController: UITextFieldDelegate {
//    
//    func textField(_ textField: UITextField, shouldChangeCharactersIn range: NSRange, replacementString string: String) -> Bool {
//        if textField == self.cardDateField {
//            //Range.Lenth will greater than 0 if user is deleting text - Allow it to replce
//            if range.length > 0
//            {
//                return true
//            }
//            
//            //Dont allow empty strings
//            if string == " "
//            {
//                return false
//            }
//            
//            //Check for max length including the spacers we added
//            if range.location >= 7
//            {
//                return false
//            }
//            
//            var originalText = textField.text
//            //Put / space after 2 digit
//            if range.location == 2
//            {
//                originalText?.append("/")
//                textField.text = originalText
//            }
//            //Verify entered text is a numeric value
//            let aSet = NSCharacterSet(charactersIn:"0123456789").inverted
//            let compSepByCharInSet = string.components(separatedBy: aSet)
//            let numberFiltered = compSepByCharInSet.joined(separator: "")
//            return string == numberFiltered
//        }
//        return true
//    }
//}
