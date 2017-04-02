//
//  RegistrationViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit

class RegistrationViewController: UIViewController {
    
    @IBOutlet weak var logoImage: UIImageView!
    @IBOutlet weak var nameField: UITextField!
    @IBOutlet weak var phoneField: UITextField!
    @IBOutlet weak var emailField: UITextField!
    @IBOutlet weak var passwordField: UITextField!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.logoImage.layer.cornerRadius = 50
    }

    @IBAction func closeRegistration(_ sender: UIButton) {
        self.dismiss(animated: true, completion: nil)
    }
    
    @IBAction func registerUser(_ sender: UIButton) {
        
        
        if let email = emailField.text,
            let password = passwordField.text,
            let name = nameField.text,
            let phone = phoneField.text {
            if email.isEmpty || password.isEmpty || name.isEmpty {
                Utils.showSimpleAlertWithTitle("Validación", message: "Favor de llenar los campos requeridos.", viewController: self)
                return
            }
            Cause.registerUserWith(name: name, phone: phone, email: email, password: password) { (succes, response, error) in
                if let data = response {
                    if let success = data["success"] as? Bool {
                        if success {
                            if let userId = data["user_id"] as? String {
                                print("user id: \(userId)")
                                UserDefaults.standard.set(userId, forKey: "userId")
                                UserDefaults.standard.synchronize()
                            }
                            self.performSegue(withIdentifier: "loginSuccess", sender: self)
                        } else {
                            print("Error Success: \(error)")
                        }
                    } else {
                        print("Error key: \(error)")
                    }
                } else {
                    print("Error call: \(error)")
                }
            }
        }
    }
}
