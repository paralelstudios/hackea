//
//  UserViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit

class UserViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        self.navigationItem.title = " "
    }

    @IBAction func userLogout(_ sender: UIButton) {
        self.dismiss(animated: true, completion: nil)
    }
}
