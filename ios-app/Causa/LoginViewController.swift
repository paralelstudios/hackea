//
//  LoginViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit

class LoginViewController: UIViewController {
    
    

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }

    @IBAction func loginUser(_ sender: UIButton) {
        self.performSegue(withIdentifier: "loginSuccess", sender: self)
    }
}
