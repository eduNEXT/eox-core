import React from 'react';
import ReactDOM from 'react-dom';
import { Tabs } from '@edx/paragon';
import { CourseTeamManagement } from './CourseTeamManagement'
import { CourseSettings } from './CourseSettings'

function CourseManagement(props) {
  return (
    <Tabs labels={["Course team management", "Course settings", "Panel 3"]}>
      <div>
        <CourseTeamManagement orgList={props.teamManagement.list_org}/>
      </div>
      <div>
        <CourseSettings
          courseKey={props.courseSettings.course_key}
          detailsFields={props.courseSettings.details_fields}
        />
      </div>
      <div>
        Panel 3
      </div>
    </Tabs>
  );
}

export class RenderReactComponent {

  constructor(properties={}) {
    Object.assign(this, {
      properties
    });
    this.renderReact();
  }

  renderReact() {
    ReactDOM.render(
      React.createElement(CourseManagement, this.properties, null),
      document.getElementById('root')
    );
  }
}

