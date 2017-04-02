//
//  HomeViewController.swift
//  Causa
//
//  Created by Pixnabi on 4/1/17.
//  Copyright © 2017 Pixnabilab. All rights reserved.
//

import UIKit

class HomeViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        self.navigationItem.title = "Inicio"
        // Do any additional setup after loading the view.
        self.tabBarController?.tabBar.unselectedItemTintColor = UIColor.white
    }

}
