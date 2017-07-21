#!/usr/bin/env swift

import Foundation

func printTeamRoster() {
    let myURLString = "http://www.redskins.com/team/roster.html"
    guard let myURL = URL(string: myURLString) else {
        print("Error: \(myURLString) doesn't seem to be a valid URL")
        return
    }

    do {
        let myHTMLString = try String(contentsOf: myURL, encoding: .ascii)
        print("HTML : \(myHTMLString)")
    } catch let error {
        print("Error: \(error)")
    }
}

printTeamRoster()
